loadSupplier();

document
.getElementById("simpanSupplier")
.addEventListener("click", simpanSupplier);

async function simpanSupplier(){

    const data = {

        nama:
        document.getElementById("namaSupplier").value,

        hp:
        document.getElementById("noHp").value,

        alamat:
        document.getElementById("alamat").value

    };

    const response = await fetch(
        "http://127.0.0.1:5000/simpan_supplier",
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

    document.getElementById("namaSupplier").value = "";
    document.getElementById("noHp").value = "";
    document.getElementById("alamat").value = "";

    loadSupplier();

}

async function loadSupplier(){

    const response = await fetch(
        "http://127.0.0.1:5000/supplier"
    );

    const supplier = await response.json();

    let html = "";

    supplier.forEach(item => {

        html += `
        <tr>
            <td>${item.nama}</td>
            <td>${item.hp}</td>
            <td>${item.alamat}</td>
        </tr>
        `;

    });

    document.getElementById("tabelSupplier").innerHTML =
    html;

}