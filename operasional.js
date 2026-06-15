async function simpanOperasional() {

    const tanggal =
    document.getElementById("tanggal").value;

    const kategori =
    document.getElementById("kategori").value;

    const keterangan =
    document.getElementById("keterangan").value;

    const jumlah =
    document.getElementById("jumlah").value;

    const response = await fetch(
        "http://127.0.0.1:5000/simpan_operasional",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                tanggal,
                kategori,
                keterangan,
                jumlah
            })
        }
    );

    const hasil = await response.json();

    alert(hasil.message);

    loadOperasional();
}

async function loadOperasional() {

    const response = await fetch(
    "http://127.0.0.1:5000/operasional"
);

    const data = await response.json();

    let html = "";

    data.forEach(item => {

        html += `
        <tr>
            <td>${item.id}</td>
            <td>${item.tanggal}</td>
            <td>${item.kategori}</td>
            <td>${item.keterangan}</td>
            <td>${item.jumlah}</td>
        </tr>
        `;
    });

    document.getElementById(
        "dataOperasional"
    ).innerHTML = html;
}
function kembaliDashboard() {
    window.location.href = "index.html";
}
loadOperasional();