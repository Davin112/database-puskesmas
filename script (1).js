const complaints = {
  "Sakit Kepala": ["Nyeri berdenyut", "Pusing/Berat", "Sensitif cahaya", "Pandangan kabur"],
  "Mual": ["Ingin muntah", "Perut tak nyaman", "Mulut pahit", "Keringat dingin"],
  "Diare": ["BAB > 3x sehari", "Kram perut", "Lemas", "Dehidrasi"],
  "Batuk & Pilek": ["Batuk kering", "Hidung tersumbat", "Sakit tenggorokan", "Demam ringan"],
  "Luka Ringan": ["Luka gores", "Memar", "Bengkak", "Perdarahan"]
};

let currentData = {};

// Fungsi pindah step
function goToStep(currentId, nextId) {
  document.getElementById(currentId).classList.remove('active');
  document.getElementById(nextId).classList.add('active');
}

// Step 1: Validasi nama dan umur
function checkIdentity() {
  const nama = document.getElementById('nama').value.trim();
  const umur = parseInt(document.getElementById('umur').value);

  if (!nama || nama.length < 4 ||!/^[a-zA-Z\s]+$/.test(nama.replace(/\s/g,''))) {
    alert('Nama minimal 4 huruf, hanya boleh A-Z');
    return;
  }
  if (!umur || umur < 1 || umur > 100) {
    alert('Umur harus 1-100');
    return;
  }

  currentData.nama = nama;
  currentData.umur = umur;
  goToStep('step-input', 'step-jalur');
}

// Step 2: Validasi jalur dan ID
function checkJalur() {
  const jalur = document.getElementById('jalur').value;
  const id_pasien = document.getElementById('id_pasien').value.trim();

  if (id_pasien.length!== 5 ||!/^\d{5}$/.test(id_pasien)) {
    alert('ID harus 5 digit angka');
    return;
  }

  currentData.jalur = jalur;
  currentData.id_pasien = id_pasien;
  goToStep('step-jalur', 'step-emergency');
}

// Step 3: Set kondisi darurat
function setEmergency(isEmergency) {
  currentData.darurat = isEmergency;
  renderGejala();
  goToStep('step-emergency', 'step-symptoms');
}

// Render checkbox gejala dengan warna
function renderGejala() {
  const list = document.getElementById('list-gejala');
  list.innerHTML = '';

  const colorMap = {
    "Sakit Kepala": "cat-kepala",
    "Mual": "cat-mual",
    "Diare": "cat-diare",
    "Batuk & Pilek": "cat-batuk",
    "Luka Ringan": "cat-luka"
  };

  for (let kategori in complaints) {
    list.innerHTML += `<div class="cat-title ${colorMap[kategori]}">${kategori}</div>`;
    complaints[kategori].forEach(gejala => {
      list.innerHTML += `
        <div class="check-item">
          <input type="checkbox" class="gejala" value="${gejala}">
          <label>${gejala}</label>
        </div>
      `;
    });
  }
}

// Step 4: Kirim data ke server
async function finalProcess() {
  const gejalaCount = document.querySelectorAll('.gejala:checked').length;
  currentData.gejala_count = gejalaCount;

  try {
    const res = await fetch('/api/daftar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(currentData)
    });

    const result = await res.json();

    if (result.sukses) {
      document.getElementById('res-nama').textContent = currentData.nama;
      document.getElementById('res-poli').textContent = result.poli;
      document.getElementById('res-nomor').textContent = result.nomor_antrian;
      document.getElementById('qr-code-box').innerHTML = `<img src="${result.qr_url}" width="180">`;
      document.getElementById('res-date').textContent = new Date().toLocaleString('id-ID');
      goToStep('step-symptoms', 'step-result');
    } else {
      alert('Gagal: ' + result.msg);
    }
  } catch (err) {
    alert('Error: ' + err.message);
  }
}

// Update label ID sesuai jalur
document.getElementById('jalur').addEventListener('change', (e) => {
  const label = document.getElementById('labelId');
  const input = document.getElementById('id_pasien');
  if (e.target.value === 'BPJS') {
    label.textContent = 'No BPJS';
    input.placeholder = '5 digit No BPJS';
  } else if (e.target.value === 'ASUR') {
    label.textContent = 'No Asuransi';
    input.placeholder = '5 digit No Asuransi';
  } else {
    label.textContent = 'NIK';
    input.placeholder = '5 digit NIK';
  }
});