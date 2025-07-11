# Usa l'immagine base di Python
FROM python:3.11-slim

# Installa Tesseract e Poppler
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev poppler-utils libxml2-dev libxslt1-dev && \
    apt-get clean

# Imposta la directory di lavoro
WORKDIR /app

# Copia il contenuto del progetto
COPY . /app

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando di avvio
CMD ["gunicorn", "--timeout", "500", "FlaskAPI_perEstrattore:app", "--bind", "0.0.0.0:5000", "--workers", "1"]
