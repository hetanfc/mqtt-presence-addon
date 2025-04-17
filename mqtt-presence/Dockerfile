ARG BUILD_FROM
FROM ${BUILD_FROM}

# Installa dipendenze necessarie: Python, pip, paho-mqtt e jq
RUN apk add --no-cache python3 py3-pip jq && \
    pip3 install --no-cache-dir paho-mqtt

# Imposta la working directory
WORKDIR /app

# Copia gli script nell'immagine
COPY mqtt_presence.py run.sh ./

# Rendi eseguibile lo script di avvio
RUN chmod +x /app/run.sh

# Avvia lo script
CMD [ "/app/run.sh" ]