FROM python:3.11-slim

# Sistem bağımlılıklarını kur (Poppler ve Tesseract için)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Önce kütüphaneleri kur (cache avantajı için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

CMD ["python", "app_main.py"]