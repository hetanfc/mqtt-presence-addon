# Usa un'immagine base leggera con Python
FROM python:3.11-slim

# Imposta la working directory
WORKDIR /app

# Installa dipendenze necessarie: paho-mqtt e jq per leggere options.json
RUN apt-get update && \
    apt-get install -y jq && \
    pip install --no-cache-dir paho-mqtt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copia gli script nell'immagine
COPY mqtt_presence.py run.sh ./

# Rendi eseguibile lo script di avvio
RUN chmod +x /app/run.sh

# Avvia lo script
CMD [ "/app/run.sh" ]