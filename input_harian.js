// ======================
// TANGGAL HARI INI
// ======================

const today = new Date();

const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");

document.getElementById("tanggal").value =
`${year}-${month}-${day}`;

// ======================
// LOAD BARANG
// ======================

loadBarang();

async function loadBarang(){

    const response = await fetch(
        "http://127.0.0.1:5000/barang"
    );

    const barang =
    await response.json();

    let html =
    '<option value="">Pilih Barang</option>';

    barang.forEach(item => {

        html += `
        <option value="${item.nama}">
            ${item.nama}
        </option>
        `;

    });

    document.getElementById("barang").innerHTML =
    html;

}

// ======================
// PILIH BARANG
// ======================

document
.getElementById("barang")
.addEventListener("change", isiDataBarang);

async function isiDataBarang(){

    const response = await fetch(
        "http://127.0.0.1:5000/barang"
    );

    const barang =
    await response.json();

    const barangDipilih =
    document.getElementById("barang").value;

    barang.forEach(item => {

        if(item.nama === barangDipilih){

            document.getElementById("stokAwal").value =
            item.stok;

            document.getElementById("hargaJual").value =
            item.harga_jual;

            document.getElementById("laba").dataset.modal =
            item.harga_beli;

        }

    });

    hitungSemua();

}

// ======================
// HITUNG OTOMATIS
// ======================

document
.getElementById("sisa")
.addEventListener("input", hitungSemua);

document
.getElementById("pengembalian")
.addEventListener("input", hitungSemua);

function hitungSemua(){

    const stokAwal =
    Number(document.getElementById("stokAwal").value) || 0;

    const sisa =
    Number(document.getElementById("sisa").value) || 0;

    const pengembalian =
    Number(document.getElementById("pengembalian").value) || 0;

    const hargaJual =
    Number(document.getElementById("hargaJual").value) || 0;

    const hargaBeli =
    Number(document.getElementById("laba").dataset.modal) || 0;

    const terjual =
    stokAwal - sisa - pengembalian;

    const omzet =
    terjual * hargaJual;

    const laba =
    terjual * (hargaJual - hargaBeli);

    document.getElementById("terjual").value =
    terjual;

    document.getElementById("omzet").value =
    omzet;

    document.getElementById("laba").value =
    laba;

}

// ======================
// SIMPAN INPUT HARIAN
// ======================

document
.getElementById("simpanBtn")
.addEventListener("click", simpanInputHarian);

async function simpanInputHarian(){

    const hargaBeli =
    Number(document.getElementById("laba").dataset.modal) || 0;

    const data = {

        tanggal:
        document.getElementById("tanggal").value,

        barang:
        document.getElementById("barang").value,

        stok_awal:
        Number(document.getElementById("stokAwal").value),

        tambahan: 0,

        sisa_stok:
        Number(document.getElementById("sisa").value),

        pengembalian:
        Number(document.getElementById("pengembalian").value),

        terjual:
        Number(document.getElementById("terjual").value),

        harga_beli:
        hargaBeli,

        harga_jual:
        Number(document.getElementById("hargaJual").value),

        omzet:
        Number(document.getElementById("omzet").value),

        modal:
        Number(document.getElementById("terjual").value)
        * hargaBeli,

        laba:
        Number(document.getElementById("laba").value)

    };

    const response = await fetch(
        "http://127.0.0.1:5000/simpan_input_harian",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }
    );

    const hasil =
    await response.json();

   alert(hasil.message);

loadData();
}
// ======================
// LOAD DATA INPUT HARIAN
// ======================

loadData();

async function loadData(){

    const response = await fetch(
        "http://127.0.0.1:5000/input_harian"
    );

    const data = await response.json();

    let html = "";

    data.forEach(item => {

        html += `
        <tr>
            <td>${item.tanggal}</td>
            <td>${item.barang}</td>
            <td>${item.stok_awal}</td>
            <td>${item.sisa_stok}</td>
            <td>${item.pengembalian}</td>
            <td>${item.terjual}</td>
            <td>Rp ${Number(item.omzet).toLocaleString()}</td>
            <td>Rp ${Number(item.laba).toLocaleString()}</td>
        </tr>
        `;

    });

    document.getElementById("dataTransaksi").innerHTML =
    html;

}