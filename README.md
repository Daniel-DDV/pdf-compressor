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
