// Tanggal Hari Ini
const today = new Date();

document.getElementById("tanggal").value =
today.toISOString().split("T")[0];

// Load Awal
loadSupplier();
loadData();

// Tombol Simpan
document
.getElementById("simpanBtn")
.addEventListener("click", simpanPembayaran);

// ======================
// LOAD SUPPLIER
// ======================
async function loadSupplier(){

    const response = await fetch(
        "http://127.0.0.1:5000/supplier"
    );

    const supplier = await response.json();

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

    document
    .getElementById("supplier")
    .addEventListener(
        "change",
        loadHutangSupplier
    );
}

// ======================
// HITUNG TOTAL PEMBAYARAN
// ======================
function hitungTotalPembayaran(){

    let total = 0;

    document
    .querySelectorAll(".cekHutang:checked")
    .forEach(item => {

        total += Number(item.dataset.nominal);

    });

    document.getElementById("nominal").value =
    total;

}

// ======================
// LOAD HUTANG SUPPLIER
// ======================
async function loadHutangSupplier(){

    const supplier =
    document.getElementById("supplier").value;

    if(!supplier){

        document.getElementById(
            "dataHutangSupplier"
        ).innerHTML = "";

        document.getElementById("nominal").value = "";

        return;
    }

    const response = await fetch(
        `http://127.0.0.1:5000/hutang_supplier/${encodeURIComponent(supplier)}`
    );

    const data =
    await response.json();

    let html = "";

    data.forEach(item => {

        html += `
        <tr>

            <td>
                <input
                    type="checkbox"
                    class="cekHutang"
                    data-id="${item.id}"
                    data-nominal="${item.sisa_hutang}"
                    onchange="hitungTotalPembayaran()"
                >
            </td>

            <td>${item.barang}</td>

            <td>
                Rp ${Number(item.sisa_hutang).toLocaleString()}
            </td>

        </tr>
        `;
    });

    document.getElementById(
        "dataHutangSupplier"
    ).innerHTML = html;

    document.getElementById("nominal").value = "";
}

// ======================
// SIMPAN PEMBAYARAN
// ======================
async function simpanPembayaran(){

    const hutangDipilih = [];

    document
    .querySelectorAll(".cekHutang:checked")
    .forEach(item => {

        hutangDipilih.push(
            Number(item.dataset.id)
        );

    });

    if(hutangDipilih.length === 0){

        alert("Pilih hutang yang akan dibayar!");

        return;
    }

    const data = {

        tanggal:
        document.getElementById("tanggal").value,

        supplier:
        document.getElementById("supplier").value,

        nominal:
        document.getElementById("nominal").value,

        keterangan:
        document.getElementById("keterangan").value,

        hutang_ids:
        hutangDipilih

    };

    const response = await fetch(
        "http://127.0.0.1:5000/simpan_pembayaran_supplier",
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify(data)
        }
    );

   const hasil = await response.json();

console.log("HASIL =", hasil);

alert(hasil.message);

window.open(
    `http://127.0.0.1:5000/cetak_pembayaran_supplier/${hasil.id}`,
    "_blank"
);

loadData();
loadHutangSupplier();
}

// ======================
// LOAD RIWAYAT PEMBAYARAN
// ======================
async function loadData(){

    const response = await fetch(
        "http://127.0.0.1:5000/pembayaran_supplier"
    );

    const data =
    await response.json();

    let html = "";

    data.forEach(item => {

       html += `
            <tr>
                <td>${item.tanggal}</td>

                <td>${item.supplier}</td>

                <td>
                    Rp ${Number(item.nominal).toLocaleString()}
                </td>

                <td>${item.keterangan}</td>

                <td>
                    <button
                        onclick="cetakPembayaran(${item.id})"
                    >
                        🖨 Cetak
                    </button>
                </td>
            </tr>
            `;

    });

    document.getElementById("dataPembayaran").innerHTML =
    html;
}
function cetakPembayaran(id){

    window.open(
        `http://127.0.0.1:5000/cetak_pembayaran_supplier/${id}`,
        "_blank"
    );

}