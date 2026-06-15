// ======================
// TANGGAL HARI INI
// ======================

const today = new Date();

const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");

document.getElementById("tanggal").value =
`${year}-${month}-${day}`;

loadLaporan();

// ======================
// LOAD LAPORAN
// ======================

async function loadLaporan(){

    const tanggal =
    document.getElementById("tanggal").value;

    const response = await fetch(
        `http://127.0.0.1:5000/laporan_harian?tanggal=${tanggal}`
    );

    const data = await response.json();

    let html = "";

    let totalOmzet = 0;
    let totalModal = 0;
    let totalLaba = 0;

    data.forEach(item => {

        totalOmzet += Number(item.omzet);
        totalModal += Number(item.modal);
        totalLaba += Number(item.laba);

        html += `
        <tr>
            <td>${item.barang}</td>
            <td>${item.stok_awal}</td>
            <td>${item.pengembalian}</td>
            <td>${item.terjual}</td>
            <td>${item.sisa_stok}</td>
            <td>Rp ${Number(item.omzet).toLocaleString()}</td>
            <td>Rp ${Number(item.modal).toLocaleString()}</td>
            <td>Rp ${Number(item.laba).toLocaleString()}</td>
        </tr>
        `;

    });

    document.getElementById("dataLaporan").innerHTML =
    html;

    document.getElementById("totalOmzet").innerHTML =
    "Rp " + totalOmzet.toLocaleString();

    document.getElementById("totalModal").innerHTML =
    "Rp " + totalModal.toLocaleString();

    document.getElementById("totalLaba").innerHTML =
    "Rp " + totalLaba.toLocaleString();

}