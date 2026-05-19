# 🏥 Sistem Manajemen Database Pasien Puskesmas

Project ini berisi rancangan basis data (database relational) menggunakan **MySQL/MariaDB** yang dirancang khusus untuk mengelola data operasional di Puskesmas. Sistem ini mencakup pengelolaan data poliklinik, dokter bertugas, identitas pasien, hingga pencatatan rekam medis (kunjungan pasien).

---

## 📌 Fitur Utama Database
* **Manajemen Poliklinik:** Memisahkan data berdasarkan unit layanan (Poli Umum, Gigi, KIA, dll).
* **Relasi Dokter & Poli:** Setiap dokter terikat pada poliklinik spesifik tempat mereka bertugas.
* **Rekam Medis (Kunjungan):** Mencatat keluhan pasien, tanda-tanda vital (tekanan darah, berat badan, suhu), diagnosa dokter, hingga resep obat yang diberikan.
* **Integritas Data:** Menggunakan *Foreign Key* dengan sistem `ON DELETE CASCADE` dan `SET NULL` untuk menjaga kebersihan data saat ada penghapusan.

---

## 🗺️ Struktur & Arsitektur Tabel

Database ini terdiri dari 4 tabel utama yang saling berelasi:

1. **`poli`** : Menyimpan daftar poliklinik di Puskesmas.
2. **`dokter`** : Menyimpan data identitas dokter dan spesialisasinya.
3. **`pasien`** : Menyimpan data demografi pasien (menggunakan NIK sebagai *unique key*).
4. **`kunjungan`** : Tabel transaksi rekam medis yang menghubungkan pasien dengan dokter yang memeriksa.

---

## 📊 Preview Data Pasien & Kunjungan

Berikut adalah contoh visualisasi data yang dihasilkan oleh database ini:

### 👤 Data Pasien Terdaftar
| ID | NIK | Nama Pasien | Jenis Kelamin | Alamat | No. Telepon |
|----|-----|-------------|---------------|--------|-------------|
| 1  | 3216001122334455 | Ahmad Dahlan | Laki-laki | Jl. Merdeka No. 10, Bekasi | 081122334455 |
| 2  | 3216009988776655 | Rina Melati | Perempuan | Jl. Mawar No. 5, Bekasi | 085566778899 |

### 📋 Rekam Medis (Kunjungan Pasien)
| Tgl Kunjungan | Nama Pasien | Dokter Pemeriksa | Keluhan | Diagnosa | Resep Obat |
|---------------|-------------|------------------|---------|----------|------------|
| 19-05-2026 | Ahmad Dahlan | dr. Budi Santoso | Demam & Sakit Kepala | Gejala Tifus | Paracetamol 500mg, Amoxicillin |
| 19-05-2026 | Rina Melati | drg. Siti Aminah | Sakit gigi berlubang | Karies Gigi | Asam Mefenamat |

---

## 🚀 Cara Menjalankan Project Secara Lokal

Jika Anda ingin menguji kodingan database ini di komputer Anda, ikuti langkah berikut:

### 1. Persiapan Server
1. Download dan instal **XAMPP**.
2. Buka XAMPP Control Panel lalu aktifkan modul **Apache** dan **MySQL** (klik tombol *Start*).

### 2. Import Database (via phpMyAdmin)
1. Buka browser lalu akses `http://localhost/phpmyadmin`.
2. Klik tab **SQL** di bagian menu atas.
3. Buka file `puskesmas.sql` yang ada di repositori ini, salin seluruh kodenya, lalu tempel ke dalam kotak SQL di phpMyAdmin.
4. Klik tombol **Kirim / Go** di pojok kanan bawah.

### 3. Import Database (via VS Code)
1. Pastikan Anda sudah menginstal ekstensi **Database Client** atau **SQLTools**.
2. Hubungkan ekstensi ke `localhost` (Username: `root`, Password: *kosong*).
3. Buka file `puskesmas.sql`, klik kanan pada area kode, lalu pilih **Run Selected Query** atau **Execute SQL**.

---

🛠️ **Teknologi yang Digunakan:** MySQL, DDL/DML SQL Script, Markdown Visualizer.
