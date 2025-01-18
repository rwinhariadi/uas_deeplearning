# Gunakan base image Python
FROM python:3.9-slim

# Set working directory di dalam container
WORKDIR /app

# Salin file requirements.txt untuk menginstal dependensi
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file dari direktori backend ke dalam container
COPY . .

# Expose port untuk Flask
EXPOSE 8080

# Jalankan aplikasi backend
CMD ["python", "app.py"]
