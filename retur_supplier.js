function hitungTotal() {

    const qty =
    Number(document.getElementById("qty").value || 0);

    const harga =
    Number(document.getElementById("harga_beli").value || 0);

    document.getElementById("total").value =
    qty * harga;
}

async function loadSupplier() {

    const response = await fetch(
        "http://127.0.0.1:5000/data_supplier"
    );

    const data = await response.json();

    let html = "";

    data.forEach(item => {

        html += `
        <option value="${item.nama}">
        `;
    });

    document.getElementById(
        "listSupplier"
    ).innerHTML = html;
}

async function loadBarang() {

    const response = await fetch(
        "http://127.0.0.1:5000/data_barang"
    );

    const data = await response.json();

    let html = "";

    data.forEach(item => {

        html += `
        <option value="${item.nama}">
        `;
    });

    document.getElementById(
        "listBarang"
    ).innerHTML = html;
}

async function ambilInfoBarang() {

    const barang =
    document.getElementById("barang").value;

    if (!barang) return;

    const response = await fetch(
        `http://127.0.0.1:5000/info_barang/${barang}`
    );

    const data =
    await response.json();

    document.getElementById(
        "harga_beli"
    ).value = data.harga_beli;

    document.getElementById(
        "qty"
    ).value = data.pengembalian;

    hitungTotal();
}

async function simpanRetur() {

    const tanggal =
    document.getElementById("tanggal").value;

    const supplier =
    document.getElementById("supplier").value;

    const barang =
    document.getElementById("barang").value;

    const qty =
    document.getElementById("qty").value;

    const harga_beli =
    document.getElementById("harga_beli").value;

    const total =
    document.getElementById("total").value;

    const keterangan =
    document.getElementById("keterangan").value;

    const response = await fetch(
        "http://127.0.0.1:5000/simpan_retur_supplier",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                tanggal,
                supplier,
                barang,
                qty,
                harga_beli,
                total,
                keterangan
            })
        }
    );

    const hasil =
    await response.json();

    alert(hasil.message);

    loadRetur();
}

async function loadRetur() {

    const response = await fetch(
        "http://127.0.0.1:5000/retur_supplier"
    );

    const data =
    await response.json();

    let html = "";

    data.forEach(item => {

        html += `
        <tr>
            <td>${item.id}</td>
            <td>${item.tanggal}</td>
            <td>${item.supplier}</td>
            <td>${item.barang}</td>
            <td>${item.qty}</td>
            <td>${item.harga_beli}</td>
            <td>${item.total}</td>
            <td>${item.keterangan}</td>
        </tr>
        `;
    });

    document.getElementById(
        "dataRetur"
    ).innerHTML = html;
}

function kembaliDashboard() {
    window.location.href = "index.html";
}

loadSupplier();
loadBarang();
loadRetur();
