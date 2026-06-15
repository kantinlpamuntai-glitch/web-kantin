loadBarang();

document
.getElementById("simpanBarang")
.addEventListener("click", simpanBarang);

async function simpanBarang() {

    const data = {
        kode: document.getElementById("kode").value,
        nama: document.getElementById("nama").value,
        hargaBeli: document.getElementById("hargaBeli").value,
        hargaJual: document.getElementById("hargaJual").value,
        stok: document.getElementById("stok").value
    };

    const response = await fetch(
        "http://127.0.0.1:5000/simpan_barang",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }
    );

    const hasil = await response.json();

    alert(hasil.message);

    document.getElementById("kode").value = "";
    document.getElementById("nama").value = "";
    document.getElementById("hargaBeli").value = "";
    document.getElementById("hargaJual").value = "";
    document.getElementById("stok").value = "";

    loadBarang();
}

async function loadBarang() {

    const response = await fetch(
        "http://127.0.0.1:5000/barang"
    );

    const barang = await response.json();

    let html = "";

    barang.forEach(item => {

        html += `
        <tr>
            <td>${item.kode}</td>
            <td>${item.nama}</td>
            <td>Rp ${Number(item.harga_beli).toLocaleString()}</td>
            <td>Rp ${Number(item.harga_jual).toLocaleString()}</td>
            <td>${item.stok}</td>
        </tr>
        `;
    });

    document.getElementById("tabelBarang").innerHTML =
    html;
}