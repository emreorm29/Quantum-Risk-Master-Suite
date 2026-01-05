# Python tabanlı hafif bir imaj kullanalım
FROM python:3.10-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem bağımlılıklarını kur (Matplotlib için gerekebilir)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kütüphaneleri kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını kopyala
COPY . .

# FastAPI ve Streamlit için portları aç
EXPOSE 8000
EXPOSE 8501

# Hem Backend'i hem Frontend'i başlatacak scripti çalıştır
CMD ["sh", "-c", "uvicorn monte-carlo-deneme:app --host 0.0.0.0 --port 8000 & streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0"]
