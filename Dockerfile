# Python 3.10 tabanlı ince bir sistem kullan
FROM python:3.10-slim

# Tesseract, Türkçe dil paketi ve Poppler'ı yükle
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tur \
    poppler-utils \
    && apt-get clean

# Çalışma dizinini ayarla
WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm kodlarını içeri kopyala
COPY . .

# Sunucuyu başlat
CMD ["uvicorn", "app_main:app", "--host", "0.0.0.0", "--port", "8000"]