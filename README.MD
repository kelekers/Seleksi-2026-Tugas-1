# Analisis Pasar Listing Properti & Real Estate (Rumah123)

### A. Author
* **Nama:** Abhinaya Rajendra Fargaz
* **NIM:** 18224087

### B. Deskripsi Singkat Topik & DBMS
Proyek ini melakukan ekstraksi data *listing* properti dari **Rumah123.com** untuk menganalisis pasar *real estate* (harga, lokasi, tipe properti, dan fasilitas). Topik ini dipilih karena data properti sangat kaya akan atribut relasional (Satu properti bisa memiliki banyak fasilitas, dimiliki oleh agen tertentu, dan berada di lokasi spesifik), sehingga sangat ideal untuk dieksplorasi ke dalam pemodelan *Database Relasional* dan *Data Warehouse*. DBMS yang digunakan untuk operasional dan *data warehousing* dalam proyek ini adalah **PostgreSQL**.

### C. Cara Menggunakan Scraper
1. Pastikan Python 3.x telah terinstal.
2. Instal *library* yang dibutuhkan dengan menjalankan: `pip install -r requirements.txt`
3. Masuk ke direktori `Data Scraping/src` dan jalankan *script*:
   ```bash
   python scraper.py
4. Script akan otomatis melakukan ekstraksi dan membagi output ke dalam folder Data Scraping/data/ dalam bentuk beberapa file JSON.

### D. Struktur File JSON
Data hasil scraping dipisah menjadi beberapa file untuk menghindari satu JSON besar:

- properti.json: Berisi entitas utama (ID, Harga, Luas Tanah, Luas Bangunan, dll).
- agen.json: Berisi daftar agen yang mengiklankan properti.
- lokasi.json: Berisi data wilayah (Kecamatan, Kota).
- fasilitas.json: Berisi array fasilitas yang tersedia (Kolam Renang, Garasi, dll).

### E. Struktur ERD & Diagram Relasional

### F. Proses Translasi ERD ke Diagram Relasional

### G. Screenshot Program

1. Bukti Data Storing

2. Bukti Data Warehouse

### H. Referensi
- Target Scraping: https://www.rumah123.com/
- Libraries: BeautifulSoup4, requests, pandas, psycopg2
- Dokumentasi PostgreSQL: https://www.postgresql.org/docs/

#### Bonus yang Dikerjakan:

[ ] Bonus 1: Data Warehouse (Star Schema)

[ ] Bonus 2: Automated Scheduling

[ ] Bonus 3: Query Optimization

#### Penggunaan AI:
