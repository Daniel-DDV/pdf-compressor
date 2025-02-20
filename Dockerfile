# Gebruik een lichtgewicht Python 3.12 image
FROM python:3.12-slim

# Installeer Ghostscript
RUN apt-get update && \
    apt-get install -y ghostscript && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stel de werkdirectory in
WORKDIR /app

# Kopieer de requirements en installeer de Python-dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van de applicatie
COPY . .

# Expose poort 8000
EXPOSE 8000

# Start de applicatie
CMD ["python", "main.py"]
