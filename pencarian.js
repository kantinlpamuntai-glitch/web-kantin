document
.getElementById("cariBtn")
.addEventListener("click", cariData);

// Enter untuk mencari
document
.getElementById("keyword")
.addEventListener("keypress", function(event){

    if(event.key === "Enter"){
        cariData();
    }

});

async function cariData(){

    const keyword =
    document.getElementById("keyword").value;

    const response = await fetch(
        `http://127.0.0.1:5000/pencarian?keyword=${keyword}`
    );

    const data =
    await response.json();

    let html = "";

    data.forEach(item => {

        html += `
        <tr>
            <td>${item.sumber}</td>
            <td>${item.keterangan}</td>
        </tr>
        `;

    });

    document.getElementById(
        "hasilPencarian"
    ).innerHTML = html;

}