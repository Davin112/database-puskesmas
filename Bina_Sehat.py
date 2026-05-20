from flask import Flask, render_template, request, jsonify
import sqlite3
import random
from datetime import datetime
import qrcode
import os
from threading import Thread

app = Flask(__name__)
DB_NAME = "bina_sehat.db"
QR_FOLDER = os.path.join("static", "qr")

os.makedirs(QR_FOLDER, exist_ok=True)

complaints = {
    "Sakit Kepala": ["Nyeri berdenyut", "Pusing/Berat", "Sensitif cahaya", "Pandangan kabur"],
    "Mual": ["Ingin muntah", "Perut tak nyaman", "Mulut pahit", "Keringat dingin"],
    "Diare": ["BAB > 3x sehari", "Kram perut", "Lemas", "Dehidrasi"],
    "Batuk & Pilek": ["Batuk kering", "Hidung tersumbat", "Sakit tenggorokan", "Demam ringan"],
    "Luka Ringan": ["Luka gores", "Memar", "Bengkak", "Perdarahan"],
}

def koneksi_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = koneksi_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pasien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            jalur TEXT NOT NULL,
            id_pasien TEXT NOT NULL,
            nama TEXT NOT NULL,
            umur INTEGER NOT NULL,
            nomor_antrian TEXT NOT NULL UNIQUE,
            poli TEXT,
            status TEXT NOT NULL DEFAULT 'registered',
            waktu_daftar TEXT NOT NULL,
            waktu_dilayani TEXT
        )
    ''')
    conn.commit()
    conn.close()

def valid_name(name):
    return name.replace(" ", "").isalpha() and len(name.replace(" ", "")) >= 4

def valid_age(age):
    return str(age).isdigit() and 1 <= int(age) <= 100

def valid_id_5digit(id_str):
    return str(id_str).isdigit() and len(str(id_str)) == 5

def classify_patient(age):
    age = int(age)
    if age <= 18:
        return "Poli Anak", "A"
    elif age >= 50:
        return "Poli Lansia", "L"
    else:
        return "Poli Umum", "U"

def get_kuota_terpakai(tanggal):
    conn = koneksi_db()
    c = conn.cursor()
    c.execute("SELECT jalur, COUNT(*) FROM pasien WHERE tanggal=? AND status='served' GROUP BY jalur", (tanggal,))
    data = dict(c.fetchall())
    conn.close()
    bpjs = data.get('BPJS', 0)
    asu = data.get('ASU', 0)
    um = data.get('UM', 0)
    return bpjs, asu, um, bpjs + asu + um

def cek_kuota_tersedia(jalur, tanggal):
    bpjs, asu, um, total = get_kuota_terpakai(tanggal)
    sisa_bpjs = 10 - bpjs
    if jalur == 'BPJS' and bpjs >= 10:
        return False, "Kuota BPJS hari ini penuh"
    if jalur == 'ASU' and asu >= 5:
        return False, "Kuota Asuransi hari ini penuh"
    if jalur == 'UM' and um >= 10:
        return False, "Kuota Umum hari ini penuh"
    if total >= 25:
        return False, "Kuota harian 25 pasien sudah penuh"
    if jalur!= 'BPJS' and total >= 25 - sisa_bpjs:
        return False, "Sisa kuota dialokasikan untuk BPJS"
    return True, "OK"

def daftar_pasien(jalur, id_pasien, nama, umur, poli):
    tanggal = datetime.now().strftime('%Y-%m-%d')
    waktu_daftar = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ok, msg = cek_kuota_tersedia(jalur, tanggal)
    if not ok:
        return False, msg, None
    conn = koneksi_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM pasien WHERE tanggal=? AND jalur=?", (tanggal, jalur))
    nomor_urut = c.fetchone()[0] + 1
    nomor_antrian = f"{jalur}-{nomor_urut}"
    try:
        c.execute('''
            INSERT INTO pasien (tanggal, jalur, id_pasien, nama, umur, nomor_antrian, poli, status, waktu_daftar)
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', (tanggal, jalur, id_pasien, nama, umur, nomor_antrian, poli, 'registered', waktu_daftar))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Data duplikat", None
    conn.close()
    return True, "Berhasil", nomor_antrian

def tandai_sudah_dicek(nomor_antrian):
    conn = koneksi_db()
    c = conn.cursor()
    c.execute("SELECT status FROM pasien WHERE nomor_antrian=?", (nomor_antrian,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "Nomor antrian tidak ditemukan"
    if row[0] == 'served':
        conn.close()
        return False, "Pasien sudah dicek dokter"
    waktu_dilayani = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("UPDATE pasien SET status='served', waktu_dilayani=? WHERE nomor_antrian=?",
              (waktu_dilayani, nomor_antrian))
    conn.commit()
    conn.close()
    return True, "Pasien berhasil ditandai sudah dicek"

def generate_qr(nama, nomor_antrian, jalur, id_pasien):
    qr_data = f"{nomor_antrian}|{jalur}|{id_pasien}|{nama}"
    qr = qrcode.make(qr_data)
    filename = f"Antrian_{nomor_antrian.replace('/', '-')}.png"
    filepath = os.path.join(QR_FOLDER, filename)
    qr.save(filepath)
    return f"/static/qr/{filename}"

# ========== ROUTE FLASK ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/daftar', methods=['POST'])
def api_daftar():
    data = request.json
    nama = data.get('nama')
    umur = data.get('umur')
    jalur = data.get('jalur')
    id_pasien = data.get('id_pasien')
    darurat = data.get('darurat', False)
    gejala_count = data.get('gejala_count', 0)
    if not valid_name(nama):
        return jsonify({'sukses': False, 'msg': 'Nama harus huruf A-Z dan minimal 4 karakter'}), 400
    if not valid_age(umur):
        return jsonify({'sukses': False, 'msg': 'Umur harus angka 1 sampai 100'}), 400
    if not valid_id_5digit(id_pasien):
        return jsonify({'sukses': False, 'msg': 'ID harus 5 digit angka'}), 400
    if darurat:
        poli = "IGD (DARURAT)"
    elif gejala_count >= 5:
        poli = "IGD (GEJALA BERAT)"
    else:
        poli, _ = classify_patient(umur)
    sukses, msg, nomor_antrian = daftar_pasien(jalur, id_pasien, nama, umur, poli)
    if sukses:
        qr_url = generate_qr(nama, nomor_antrian, jalur, id_pasien)
        return jsonify({'sukses': True, 'nama': nama, 'poli': poli, 'nomor_antrian': nomor_antrian, 'jalur': jalur, 'qr_url': qr_url})
    else:
        return jsonify({'sukses': False, 'msg': msg}), 400

@app.route('/api/cek_dokter', methods=['POST'])
def api_cek_dokter():
    data = request.json
    nomor = data.get('nomor_antrian')
    sukses, msg = tandai_sudah_dicek(nomor)
    return jsonify({'sukses': sukses, 'msg': msg})

@app.route('/api/kuota')
def api_kuota():
    tanggal = datetime.now().strftime('%Y-%m-%d')
    bpjs, asu, um, total = get_kuota_terpakai(tanggal)
    return jsonify({'tanggal': tanggal, 'bpjs': {'terpakai': bpjs, 'max': 10}, 'asuransi': {'terpakai': asu, 'max': 5}, 'umum': {'terpakai': um, 'max': 10}, 'total': {'terpakai': total, 'max': 25}, 'sisa': 25 - total})

# ========== FUNGSI CLI LAMA ==========
def menu_daftar():
    print("\nPilih Jalur Pendaftaran:")
    print("[1] BPJS")
    print("[2] Umum")
    print("[3] Asuransi")
    jalur_pil = input("Pilih: ")
    jalur_map = {"1": "BPJS", "2": "UM", "3": "ASU"}
    if jalur_pil not in jalur_map:
        print("⚠️ Pilihan jalur tidak valid!")
        return
    jalur = jalur_map[jalur_pil]
    while True:
        nama = input("Masukkan Nama Lengkap (Min. 4 huruf): ")
        if valid_name(nama): break
        print("⚠️ Nama harus huruf A-Z dan minimal 4 karakter!")
    while True:
        umur_input = input("Masukkan Umur Pasien (1-100): ")
        if valid_age(umur_input): break
        print("⚠️ Umur harus angka 1 sampai 100!")
    if jalur == "BPJS":
        while True:
            id_pasien = input("Masukkan No. BPJS [5 digit]: ")
            if valid_id_5digit(id_pasien): break
            print("⚠️ No. BPJS harus 5 digit angka!")
    elif jalur == "UM":
        while True:
            id_pasien = input("Masukkan NIK [5 digit]: ")
            if valid_id_5digit(id_pasien): break
            print("⚠️ NIK harus 5 digit angka!")
    else:
        while True:
            id_pasien = input("Masukkan No. Asuransi [5 digit]: ")
            if valid_id_5digit(id_pasien): break
            print("⚠️ No. Asuransi harus 5 digit angka!")
    darurat = input("\nApakah pasien dalam kondisi darurat/kritis? (y/n): ").lower()
    if darurat == "y":
        poli = "IGD (DARURAT)"
        gejala_count = 0
    else:
        print("\n--- Pilih Gejala ---")
        gejala_count = 0
        for category, symptoms in complaints.items():
            print(f"\n[{category}]")
            for symptom in symptoms:
                jawab = input(f"Apakah mengalami '{symptom}'? (y/n): ").lower()
                if jawab == "y": gejala_count += 1
        if gejala_count >= 5:
            poli = "IGD (GEJALA BERAT)"
        else:
            poli_name, _ = classify_patient(umur_input)
            poli = poli_name
    sukses, msg, hasil = daftar_pasien(jalur, id_pasien, nama, umur_input, poli)
    if sukses:
        print_receipt(nama, poli, hasil, jalur, id_pasien)
        print(f"\n✅ Berhasil daftar! Nomor antrian: {hasil}")
    else:
        print(f"\n❌ Gagal: {msg}")

def menu_cek_dokter():
    nomor = input("Masukkan nomor antrian: ")
    sukses, msg = tandai_sudah_dicek(nomor)
    print(f"\n{msg}")

def menu_kuota():
    tanggal = datetime.now().strftime('%Y-%m-%d')
    bpjs, asu, um, total = get_kuota_terpakai(tanggal)
    print(f"\n=== KUOTA HARI INI {tanggal} ===")
    print(f"BPJS : {bpjs}/10")
    print(f"Asuransi: {asu}/5")
    print(f"Umum : {um}/10")
    print(f"Total : {total}/25")
    print(f"Sisa : {25 - total}")

def print_receipt(nama, poli, nomor_antrian, jalur, id_pasien):
    print("\n===================================")
    print(" PUSKESMAS BINA SEHAT")
    print("====================================")
    print(f"Jalur : {jalur}")
    print(f"ID : {id_pasien}")
    print(f"Pasien: {nama}")
    print(f"Poli : {poli}")
    print(f"Nomor : {nomor_antrian}")
    print(f"Waktu : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("====================================")
    generate_qr(nama, nomor_antrian, jalur, id_pasien)

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ========== MAIN ==========
if __name__ == "__main__":
    init_db()
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("====================================")
    print(" Server Web jalan di http://localhost:5000")
    print(" Mode Terminal aktif")
    print("====================================")

    while True:
        print("\n====================================")
        print(" PUSKESMAS BINA SEHAT - SYSTEM")
        print("====================================")
        print("1. Daftar Antrian")
        print("2. Cek Dokter / Selesai")
        print("3. Lihat Kuota Hari Ini")
        print("4. Keluar")
        menu = input("Pilih Menu: ")
        if menu == "1":
            menu_daftar()
        elif menu == "2":
            menu_cek_dokter()
        elif menu == "3":
            menu_kuota()
        elif menu == "4":
            print("Terima kasih!")
            break
        else:
            print("Menu tidak valid!")