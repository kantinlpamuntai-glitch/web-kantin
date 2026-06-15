loadStok();

async function loadStok(){

    const response = await fetch(
        "http://127.0.0.1:5000/barang"
    );

    const barang = await response.json();

    let html = "";

    let totalNilaiStok = 0;
    let totalPotensi = 0;

    barang.forEach(item => {

        const stok =
        Number(item.stok);

        const hargaBeli =
        Number(item.harga_beli);

        const hargaJual =
        Number(item.harga_jual);

        const nilaiStok =
        stok * hargaBeli;

        const potensiPenjualan =
        stok * hargaJual;

        totalNilaiStok += nilaiStok;
        totalPotensi += potensiPenjualan;

        html += `
        <tr>
            <td>${item.kode}</td>
            <td>${item.nama}</td>
            <td>${stok}</td>
            <td>Rp ${hargaBeli.toLocaleString()}</td>
            <td>Rp ${hargaJual.toLocaleString()}</td>
            <td>Rp ${nilaiStok.toLocaleString()}</td>
            <td>Rp ${potensiPenjualan.toLocaleString()}</td>
        </tr>
        `;
    });

    html += `
    <tr style="font-weight:bold;">
        <td colspan="5">TOTAL</td>
        <td>Rp ${totalNilaiStok.toLocaleString()}</td>
        <td>Rp ${totalPotensi.toLocaleString()}</td>
    </tr>
    `;

    document.getElementById("tabelStok").innerHTML =
    html;
}