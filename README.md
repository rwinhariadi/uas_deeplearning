# Aplikasi Web Pendeteksi Kematangan Pisang Menggunakan CNN

## Requirements
- Docker harus sudah terinstall
- Penyimpanan minimal 5 GB
- Kuota internet minimal 1.1 GB (untuk mengunduh library TensorFlow pada Docker)

## Cara Menjalankan Aplikasi

### 1. Menjalankan Docker Image dari Terminal atau Docker Desktop
- Jalankan Docker Desktop terlebih dahulu, jika belum aktif
- Jalankan perintah berikut pada terminal:
  - ```docker pull erwinhariadi/devops_pisang:latest```
  - ```docker run -it --name devops_container -p 8080:8080 erwinhariadi/devops_pisang```
- Setelah menjalankan perintah di atas, buka browser Anda dan akses aplikasi di:
  - <http://localhost:8080>

### 2. Membangun Docker Image Secara Lokal
- Clone repository ini
  - ```git clone https://github.com/rwinhariadi/DevOps_Pisang.git```
- Masuk ke direktori proyek
  - ```cd DevOps_Pisang```
- Bangun Docker Image
  - ```docker build -t <docker_username_anda>/devops_pisang:latest .```
- Jalankan container
  - ```docker run -it --name devops_container -p 8080:8080 <docker_username_anda>/devops_pisang```
- Setelah itu, buka browser Anda dan akses aplikasi di:
  - <http://localhost:8080>

### 3. Menjalankan Aplikasi Secara Lokal (Tanpa Docker)
- Clone repository ini
  - ```git clone https://github.com/rwinhariadi/DevOps_Pisang.git```
- Masuk ke direktori proyek
  - ```cd DevOps_Pisang```
- Jalankan aplikasi
  - ```python app/app.py```
- Setelah itu, buka browser Anda dan akses aplikasi di:
  - <http://localhost:8080>
