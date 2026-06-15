loadDashboard();

async function loadDashboard() {

    const response = await fetch(
        "http://127.0.0.1:5000/dashboard"
    );

    const data = await response.json();

    // Omzet
document.getElementById("omzet").innerHTML =
    "Rp " + Number(data.omzet).toLocaleString();

// Laba
document.getElementById("laba").innerHTML =
    "Rp " + Number(data.laba).toLocaleString();

// Saldo Kas
document.getElementById("saldoKas").innerHTML =
    "Rp " + Number(data.saldo_kas || 0).toLocaleString();

    // Hutang Supplier
    if (document.getElementById("hutangSupplier")) {
        document.getElementById("hutangSupplier").innerHTML =
            "Rp " + Number(data.hutang_supplier).toLocaleString();
    }

    // Stok Menipis
document.getElementById("stokMenipis").innerHTML =
    data.stok_menipis + " Barang";

let daftar = "";

if(data.daftar_stok_menipis){

    data.daftar_stok_menipis
        .split("<br>")
        .forEach(item => {

            daftar += `<li>${item}</li>`;

        });

}

document.getElementById(
    "daftarStokMenipis"
).innerHTML = daftar;

    // Aset Kotor
    if (document.getElementById("asetKotor")) {
        document.getElementById("asetKotor").innerHTML =
            "Rp " + Number(data.aset_kotor || 0).toLocaleString();
    }

    // Aset Bersih
    if (document.getElementById("asetBersih")) {
        document.getElementById("asetBersih").innerHTML =
            "Rp " + Number(data.aset_bersih || 0).toLocaleString();
    }

    // Persediaan
    if (document.getElementById("persediaan")) {
        document.getElementById("persediaan").innerHTML =
            "Rp " + Number(data.persediaan).toLocaleString();
    }
}

function bukaOperasional() {
    window.location.href = "operasional.html";
}
async function jalankanAutoMutasi(){

    try{

        alert("Sedang mengimpor mutasi...");

        const response =
            await fetch("/auto_mutasi");

        const hasil =
            await response.json();

        if(hasil.status === "success"){

            alert(
                "✅ " + hasil.pesan
            );

        }
        else if(hasil.status === "warning"){

            alert(
                "⚠️ " + hasil.pesan
            );

        }
        else{

            alert(
                "❌ " + hasil.pesan
            );

        }

    }
    catch(error){

        console.error(error);

        alert(
            "❌ Gagal menjalankan Auto Mutasi"
        );

    }

}
function bukaWhatsapp(){

    window.open(
        "whatsapp://send",
        "_self"
    );

}
function logout(){
    window.location.href="/logout";
}