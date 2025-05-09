# Usa l'immagine base di Python
FROM python:3.11-slim

# Installa Tesseract e Poppler
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev poppler-utils && \
    apt-get clean &&\
    fallocate -l 5G /swapfile && \
    chmod 600 /swapfile && \
    mkswap /swapfile && \
    swapon /swapfile

# Imposta la directory di lavoro
WORKDIR /app

# Copia il contenuto del progetto
COPY . /app

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando di avvio
CMD ["python", "/app/FlaskAPI_perEstrattore.py"]

#["gunicorn", "FlaskAPI_perEstrattore:app", "--bind", "0.0.0.0:5000", "--workers", "1"]
