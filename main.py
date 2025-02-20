from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import aiofiles
from datetime import datetime
import logging
import subprocess
import shutil
import os
import fitz  # PyMuPDF
from PIL import Image
import io

app = FastAPI(title="Dynamic PDF Compressor")

# CORS-configuratie
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pas aan in productie!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basis paden
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"
LOG_DIR = BASE_DIR / "logs"
for p in [UPLOAD_DIR, PROCESSED_DIR, LOG_DIR]:
    p.mkdir(exist_ok=True)

# Logging instellen
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

# Serveer statische bestanden (voor index.html, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pas het target aan naar 25 MB
TARGET_SIZE = 25 * 1024 * 1024  # 25 MB

def analyze_pdf(input_pdf: Path) -> dict:
    """
    Analyseer de PDF en retourneer statistieken:
      - total_pages: aantal pagina's
      - total_text: totaal aantal karakters op alle pagina's
      - image_count: totaal aantal images (via get_images)
    """
    doc = fitz.open(input_pdf)
    total_pages = len(doc)
    total_text = 0
    image_count = 0
    for page in doc:
        text = page.get_text()
        total_text += len(text)
        image_count += len(page.get_images(full=True))
    doc.close()
    return {"total_pages": total_pages, "total_text": total_text, "image_count": image_count}

def run_ghostscript(input_pdf: Path, output_pdf: Path, quality: str, extra_params: list = None) -> None:
    """
    Roep Ghostscript aan met een basiscommandoregel plus eventuele extra parameters.
    quality kan bijvoorbeeld zijn: "/ebook" of "/screen".
    """
    command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={quality}",
    ]
    if extra_params:
        command.extend(extra_params)
    command.extend([
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_pdf}",
        str(input_pdf)
    ])
    logging.info(f"Running Ghostscript: {' '.join(command)}")
    subprocess.run(command, check=True)

def standard_optimization(input_pdf: Path, output_pdf: Path) -> (int, Path):
    """
    Probeer eerst een standaard optimalisatie (via Ghostscript met /ebook en downsampling).
    Retourneer de bestandsgrootte en de tijdelijke output.
    """
    temp_out = output_pdf.with_suffix(".std.pdf")
    extra = [
        "-dColorImageDownsampleType=/Bicubic",
        "-dColorImageResolution=72",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dGrayImageResolution=72",
        "-dMonoImageDownsampleType=/Subsample",
        "-dMonoImageResolution=72",
    ]
    run_ghostscript(input_pdf, temp_out, quality="/ebook", extra_params=extra)
    size = temp_out.stat().st_size
    logging.info(f"Standaard optimalisatie resultaat: {size} bytes")
    return size, temp_out

def aggressive_optimization(input_pdf: Path, output_pdf: Path) -> (int, Path):
    """
    Gebruik een agressievere Ghostscript-instelling (bijv. /screen).
    Retourneer de bestandsgrootte en de tijdelijke output.
    """
    temp_out = output_pdf.with_suffix(".agg.pdf")
    extra = [
        "-dColorImageDownsampleType=/Bicubic",
        "-dColorImageResolution=72",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dGrayImageResolution=72",
        "-dMonoImageDownsampleType=/Subsample",
        "-dMonoImageResolution=72",
    ]
    run_ghostscript(input_pdf, temp_out, quality="/screen", extra_params=extra)
    size = temp_out.stat().st_size
    logging.info(f"Agressieve optimalisatie resultaat: {size} bytes")
    return size, temp_out

def dynamic_compress(input_pdf: Path, output_pdf: Path) -> dict:
    """
    Dynamische compressie:
      1. Als het bestand al ≤ target is, kopieer dan direct.
      2. Analyseer de PDF.
      3. Kies een methode:
         - Als de PDF veel tekst bevat (en weinig afbeeldingen), gebruik dan standaard optimalisatie.
         - Anders, gebruik agressieve optimalisatie.
      4. Vergelijk beide methoden en kies de kleinste.
    """
    original_size = input_pdf.stat().st_size
    if original_size <= TARGET_SIZE:
        shutil.copyfile(input_pdf, output_pdf)
        return {
            "success": True,
            "original_size": original_size,
            "compressed_size": original_size,
            "reduction_percentage": 0.0,
            "method": "geen compressie",
            "warning": "Bestand was al kleiner dan target."
        }
    stats = analyze_pdf(input_pdf)
    avg_text = stats["total_text"] / stats["total_pages"] if stats["total_pages"] > 0 else 0
    image_ratio = stats["image_count"] / stats["total_pages"] if stats["total_pages"] > 0 else 0
    logging.info(f"PDF-analyse: {stats}")

    # Beslis welke methode:
    if avg_text > 500 and image_ratio < 0.2:
        logging.info("Kies standaard optimalisatie (text-heavy document).")
        std_size, std_file = standard_optimization(input_pdf, output_pdf)
        best_method = "standaard"
        best_size = std_size
        best_file = std_file
    else:
        logging.info("Kies agressieve optimalisatie (image-heavy of gemengd document).")
        agg_size, agg_file = aggressive_optimization(input_pdf, output_pdf)
        best_method = "agressief"
        best_size = agg_size
        best_file = agg_file

    # Probeer beide methoden en kies de kleinste
    std_size, std_file = standard_optimization(input_pdf, output_pdf.with_suffix(".std.pdf"))
    agg_size, agg_file = aggressive_optimization(input_pdf, output_pdf.with_suffix(".agg.pdf"))
    if std_size <= agg_size:
        best_size = std_size
        best_method = "standaard"
        best_file = std_file
        if agg_file.exists():
            os.remove(str(agg_file))
    else:
        best_size = agg_size
        best_method = "agressief"
        best_file = agg_file
        if std_file.exists():
            os.remove(str(std_file))
    shutil.move(str(best_file), str(output_pdf))
    reduction = ((original_size - best_size) / original_size) * 100

    return {
        "success": True,
        "original_size": original_size,
        "compressed_size": best_size,
        "reduction_percentage": reduction,
        "method": best_method
    }

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Alleen PDF-bestanden worden ondersteund")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = UPLOAD_DIR / f"{timestamp}_{file.filename}"
    output_path = PROCESSED_DIR / f"compressed_{timestamp}_{file.filename}"
    try:
        async with aiofiles.open(input_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        result = dynamic_compress(input_path, output_path)
        if result["success"]:
            return {
                "message": "Bestand succesvol verwerkt",
                "original_size": result["original_size"],
                "compressed_size": result["compressed_size"],
                "reduction_percentage": result["reduction_percentage"],
                "download_path": f"/download/{output_path.name}",
                "method": result.get("method")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logging.error(f"Fout bij verwerking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if input_path.exists():
            input_path.unlink()

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = PROCESSED_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Bestand niet gevonden")
    return FileResponse(str(file_path), media_type="application/pdf", filename=file_path.name)

if __name__ == "__main__":
    import threading, webbrowser, time
    def open_browser():
        time.sleep(1)
        webbrowser.open("http://localhost:8000/static/index.html")
    threading.Thread(target=open_browser).start()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
