#!/bin/bash
set -e

echo "Aggiornamento dei pacchetti..."
apt-get update -y

echo "Installazione di Poppler e Tesseract..."
apt-get install -y poppler-utils tesseract-ocr

echo "Installazione completata!"
