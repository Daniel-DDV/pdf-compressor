```markdown
# Dynamic PDF Compressor

Dynamic PDF Compressor is een FastAPI-gebaseerde applicatie die PDF-bestanden dynamisch comprimeert met behulp van Ghostscript. De applicatie analyseert de inhoud van een PDF (tekst versus afbeeldingen) en kiest automatisch de beste compressiemethode om het bestand rond 8 MB te krijgen.

## Features

- **Dynamische compressie:** Analyseert de PDF en kiest automatisch de optimale compressiemethode.
- **Ghostscript-integratie:** Comprimeert PDF's via Ghostscript met verschillende kwaliteitsinstellingen.
- **Moderne UI:** Een gebruiksvriendelijke interface met drag-and-drop en duidelijke feedback.
- **Docker-ready:** Eenvoudig te deployen op zowel Linux als Windows met Docker.

## Prerequisites

- **Docker**  
  Zorg dat Docker is geïnstalleerd op je machine.  
  - [Docker voor Linux](https://docs.docker.com/engine/install/)
  - [Docker voor Windows](https://docs.docker.com/docker-for-windows/)

## Installatie en gebruik met Docker

1. **Clone de repository**

   ```bash
   git clone https://github.com/Daniel-DDV/pdf-compressor.git
   cd pdf-compressor
   ```

2. **Bouw de Docker-image**

   Open een terminal in de projectmap en voer uit:

   ```bash
   docker build -t pdf-compressor .
   ```

3. **Run de Docker-container**

   ```bash
   docker run -d -p 8000:8000 pdf-compressor
   ```

4. **Open de applicatie**

   Open in je browser [http://localhost:8000](http://localhost:8000) (of [http://127.0.0.1:8000](http://127.0.0.1:8000)) om de frontend te zien en een PDF te uploaden.

## Lokale installatie (zonder Docker)

### Voor Linux/WSL

1. **Clone de repository**

   ```bash
   git clone https://github.com/Daniel-DDV/pdf-compressor.git
   cd pdf-compressor
   ```

2. **Maak een virtuele omgeving aan en activeer deze**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installeer de vereiste Python-pakketten**

   ```bash
   pip install -r requirements.txt
   ```

4. **Installeer Ghostscript**

   Op Ubuntu/WSL:
   ```bash
   sudo apt-get update
   sudo apt-get install ghostscript
   ```

5. **Start de applicatie**

   ```bash
   python main.py
   ```

### Voor Windows (zonder Docker)

1. **Clone de repository** via Git Bash of een andere terminal:
   ```bash
   git clone https://github.com/Daniel-DDV/pdf-compressor.git
   cd pdf-compressor
   ```

2. **Maak een virtuele omgeving aan en activeer deze**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Installeer de vereiste Python-pakketten**

   ```bash
   pip install -r requirements.txt
   ```

4. **Installeer Ghostscript**  
   Download en installeer Ghostscript voor Windows van:  
   [https://ghostscript.com/releases/gsdnld.html](https://ghostscript.com/releases/gsdnld.html)  
   Zorg dat het installatiepad is toegevoegd aan de PATH-variabele.

5. **Start de applicatie**

   ```bash
   python main.py
   ```

## Contributing

Feedback, issues en pull requests zijn welkom! Open een issue of doe een pull request als je wilt bijdragen aan dit project.

## License

Dit project is gelicentieerd onder de MIT License.
```

---
