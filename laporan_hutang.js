loadHutang();

async function loadHutang() {

    const response = await fetch(
        "http://127.0.0.1:5000/laporan_hutang"
    );

    const data = await response.json();

    let html = "";

    let totalHutang = 0;

    data.forEach(item => {

        totalHutang += Number(item.sisa_hutang);

        html += `
        <tr>
            <td>${item.tanggal}</td>
            <td>${item.supplier}</td>
            <td>${item.barang}</td>

            <td>
                Rp ${Number(item.total).toLocaleString()}
            </td>

            <td>
                Rp ${Number(item.sudah_dibayar).toLocaleString()}
            </td>

            <td>
                Rp ${Number(item.retur).toLocaleString()}
            </td>

            <td>
                Rp ${Number(item.sisa_hutang).toLocaleString()}
            </td>
        </tr>
        `;
    });

    document.getElementById("dataHutang").innerHTML =
    html;

    document.getElementById("totalHutang").innerHTML =
    "Rp " + totalHutang.toLocaleString();
}