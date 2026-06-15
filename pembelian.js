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
// LOAD AWAL
// ======================

loadSupplierDropdown();
loadBarangDropdown();
loadData();

// ======================
// HITUNG TOTAL
// ======================

const qty = document.getElementById("qty");
const harga = document.getElementById("harga");
const total = document.getElementById("total");

function hitungTotal() {

    total.value =
    (qty.value || 0) *
    (harga.value || 0);

}

qty.addEventListener("input", hitungTotal);
harga.addEventListener("input", hitungTotal);

// ======================
// SIMPAN PEMBELIAN
// ======================

document
.getElementById("simpanBtn")
.addEventListener("click", simpanPembelian);

async function simpanPembelian(){

    const data = {

        tanggal:
        document.getElementById("tanggal").value,

        supplier:
        document.getElementById("supplier").value,

        barang:
        document.getElementById("barang").value,

        qty:
        document.getElementById("qty").value,

        harga:
        document.getElementById("harga").value,

        status:
        document.getElementById("status").value,

        total:
        document.getElementById("total").value

    };

    const response = await fetch(
        "http://127.0.0.1:5000/simpan_pembelian",
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
// TAMPIL DATA PEMBELIAN
// ======================

async function loadData(){

    const response = await fetch(
        "http://127.0.0.1:5000/pembelian"
    );

    const pembelian =
    await response.json();

    let html = "";

    pembelian.forEach(item => {

        html += `
        <tr>
            <td>${item.tanggal}</td>
            <td>${item.supplier}</td>
            <td>${item.barang}</td>
            <td>${item.qty}</td>
            <td>Rp ${Number(item.harga).toLocaleString()}</td>
            <td>${item.status}</td>
            <td>Rp ${Number(item.total).toLocaleString()}</td>
        </tr>
        `;

    });

    document.getElementById("dataPembelian").innerHTML =
    html;

}

// ======================
// DROPDOWN SUPPLIER
// ======================

async function loadSupplierDropdown(){

    const response = await fetch(
        "http://127.0.0.1:5000/supplier"
    );

    const supplier =
    await response.json();

    let html =
    '<option value="">Pilih Supplier</option>';

    supplier.forEach(item => {

        html += `
        <option value="${item.nama}">
            ${item.nama}
        </option>
        `;

    });

    document.getElementById("supplier").innerHTML =
    html;

}

// ======================
// DROPDOWN BARANG
// ======================

async function loadBarangDropdown(){

    const response = await fetch(
        "http://127.0.0.1:5000/barang"
    );

    const barang =
    await response.json();

    let html =
    '<option value="">Pilih Barang</option>';

    barang.forEach(item => {

        html += `
        <option
            value="${item.nama}"
            data-harga="${item.harga_beli}">
            ${item.nama}
        </option>
        `;

    });

    document.getElementById("barang").innerHTML =
    html;

}

// ======================
// AUTO ISI HARGA
// ======================

document
.getElementById("barang")
.addEventListener("change", isiHargaBarang);

async function isiHargaBarang(){

    const response = await fetch(
        "http://127.0.0.1:5000/barang"
    );

    const barangList =
    await response.json();

    const barangDipilih =
    document.getElementById("barang").value;

    barangList.forEach(item => {

        if(item.nama === barangDipilih){

            document.getElementById("harga").value =
            item.harga_beli;

            hitungTotal();

        }

    });

}