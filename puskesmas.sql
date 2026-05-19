-- Hapus database jika sudah ada sebelumnya, lalu buat ulang
DROP DATABASE IF EXISTS puskesmas_db;
CREATE DATABASE puskesmas_db;
USE puskesmas_db;

-- (Lanjutkan dengan kode CREATE TABLE poli, dst di bawahnya...)

-- 1. Tabel Poli (Daftar Poliklinik di Puskesmas)
CREATE TABLE poli (
    id_poli INT AUTO_INCREMENT PRIMARY KEY,
    nama_poli VARCHAR(50) NOT NULL,
    keterangan TEXT
);

-- 2. Tabel Dokter
CREATE TABLE dokter (
    id_dokter INT AUTO_INCREMENT PRIMARY KEY,
    nama_dokter VARCHAR(100) NOT NULL,
    spesialisasi VARCHAR(50),
    id_poli INT,
    no_telepon VARCHAR(15),
    FOREIGN KEY (id_poli) REFERENCES poli(id_poli) ON DELETE SET NULL
);

-- 3. Tabel Pasien
CREATE TABLE pasien (
    id_pasien INT AUTO_INCREMENT PRIMARY KEY,
    nik VARCHAR(16) UNIQUE NOT NULL,
    nama_pasien VARCHAR(100) NOT NULL,
    tempat_lahir VARCHAR(50),
    tanggal_lahir DATE,
    jenis_kelamin ENUM('Laki-laki', 'Perempuan') NOT NULL,
    golongan_darah ENUM('A', 'B', 'AB', 'O', 'Tidak Tahu') DEFAULT 'Tidak Tahu',
    alamat TEXT,
    no_telepon VARCHAR(15),
    tanggal_daftar TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabel Kunjungan (Rekam Medis)
CREATE TABLE kunjungan (
    id_kunjungan INT AUTO_INCREMENT PRIMARY KEY,
    id_pasien INT NOT NULL,
    id_dokter INT NOT NULL,
    tanggal_kunjungan DATETIME DEFAULT CURRENT_TIMESTAMP,
    keluhan TEXT NOT NULL,
    tekanan_darah VARCHAR(10),
    berat_badan DECIMAL(5,2), -- dalam kg
    suhu_tubuh DECIMAL(4,2),  -- dalam celcius
    diagnosa TEXT,
    tindakan TEXT,
    resep_obat TEXT,
    status_kunjungan ENUM('Menunggu', 'Diperiksa', 'Selesai') DEFAULT 'Menunggu',
    FOREIGN KEY (id_pasien) REFERENCES pasien(id_pasien) ON DELETE CASCADE,
    FOREIGN KEY (id_dokter) REFERENCES dokter(id_dokter) ON DELETE CASCADE
);

-- ==========================================
-- CONTOH DATA (DML - Untuk Uji Coba)
-- ==========================================

-- Insert Poli
INSERT INTO poli (nama_poli, keterangan) VALUES 
('Poli Umum', 'Pelayanan kesehatan umum'),
('Poli Gigi', 'Pelayanan kesehatan gigi dan mulut'),
('Poli KIA', 'Kesehatan Ibu dan Anak');

-- Insert Dokter
INSERT INTO dokter (nama_dokter, spesialisasi, id_poli, no_telepon) VALUES 
('dr. Budi Santoso', 'Dokter Umum', 1, '081234567890'),
('drg. Siti Aminah', 'Dokter Gigi', 2, '089876543210');

-- Insert Pasien
INSERT INTO pasien (nik, nama_pasien, tempat_lahir, tanggal_lahir, jenis_kelamin, alamat, no_telepon) VALUES 
('3216001122334455', 'Ahmad Dahlan', 'Bekasi', '1990-05-15', 'Laki-laki', 'Jl. Merdeka No. 10, Bekasi', '081122334455'),
('3216009988776655', 'Rina Melati', 'Jakarta', '1995-10-20', 'Perempuan', 'Jl. Mawar No. 5, Bekasi', '085566778899');

-- Insert Kunjungan
INSERT INTO kunjungan (id_pasien, id_dokter, keluhan, tekanan_darah, berat_badan, suhu_tubuh, diagnosa, resep_obat, status_kunjungan) VALUES 
(1, 1, 'Demam dan sakit kepala sejak 2 hari lalu', '120/80', 65.5, 38.5, 'Gejala Tifus', 'Paracetamol 500mg, Amoxicillin', 'Selesai'),
(2, 2, 'Sakit gigi berlubang bagian bawah', '110/70', 50.0, 36.5, 'Karies Gigi', 'Asam Mefenamat', 'Selesai');