# Gunakan base image untuk server static (nginx)
FROM nginx:alpine

# Hapus default konfigurasi Nginx
RUN rm -rf /usr/share/nginx/html/*

# Salin file frontend ke dalam Nginx
COPY . /usr/share/nginx/html/

# Expose port untuk frontend
EXPOSE 80

# Jalankan Nginx
CMD ["nginx", "-g", "daemon off;"]
