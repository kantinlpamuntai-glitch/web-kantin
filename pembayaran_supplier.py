from flask import request, jsonify
from app import app, conn


# =========================
# DATA PEMBAYARAN SUPPLIER
# =========================

@app.route("/pembayaran_supplier", methods=["GET"])
def get_pembayaran_supplier():

    cur = conn.cursor()

    cur.execute("""
        SELECT
        tanggal,
        supplier,
        nominal,
        keterangan
        FROM pembayaran_supplier
        ORDER BY tanggal DESC
    """)

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:
        data.append({
            "tanggal": str(row[0]),
            "supplier": row[1],
            "nominal": float(row[2]),
            "keterangan": row[3]
        })

    return jsonify(data)


# =========================
# SIMPAN PEMBAYARAN SUPPLIER
# =========================

@app.route("/simpan_pembayaran_supplier", methods=["POST"])
def simpan_pembayaran_supplier():

    data = request.get_json()

    cur = conn.cursor()

    # Simpan pembayaran supplier
    cur.execute("""
        INSERT INTO pembayaran_supplier
        (tanggal,supplier,nominal,keterangan)
        VALUES (%s,%s,%s,%s)
    """, (
        data["tanggal"],
        data["supplier"],
        data["nominal"],
        data["keterangan"]
    ))

    # Kurangi kas
    cur.execute("""
        INSERT INTO kas
        (tanggal,keterangan,masuk,keluar)
        VALUES (%s,%s,%s,%s)
    """, (
        data["tanggal"],
        "PEMBAYARAN SUPPLIER",
        0,
        data["nominal"]
    ))

    conn.commit()
    cur.close()

    return jsonify({
        "message": "Pembayaran supplier berhasil disimpan"
    })