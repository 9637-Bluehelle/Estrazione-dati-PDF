#!/bin/bash
set -e

echo "Aggiornamento dei pacchetti..."
sudo apt-get update -y

echo "Installazione di Poppler e Tesseract..."
sudo apt-get install -y poppler-utils tesseract-ocr

echo "Installazione completata!"