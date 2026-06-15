from flask import Flask, jsonify, redirect, send_from_directory, render_template, request, send_file, session
from flask_cors import CORS
import psycopg2

import os
import glob
import io

import pandas as pd
from openpyxl import load_workbook
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)
app = Flask(__name__)
CORS(app) 

app.secret_key = "delbar_secret"
@app.route("/")
def home():

    if "user" not in session:

        return redirect("/login.html")

    return send_from_directory(
        ".",
        "index.html"
    )

@app.route('/laporan_tarik_tunai')
def laporan_tarik_tunai():
    return render_template(
        'laporan_tarik_tunai.html'
    )
@app.route('/laporan_mutasi_brilink')
def laporan_mutasi_brilink():

    return render_template(
        'laporan_mutasi_brilink.html'
    )
@app.route("/<path:nama_file>")
def static_files(nama_file):
    return send_from_directory(".", nama_file)    

conn = psycopg2.connect(
    host="localhost",
    database="delbar",
    user="postgres",
    password="yahyabarus43"
)

def hitung_admin(nominal):

    if nominal <= 120000:
        return 5000

    return ((nominal - 120001) // 100000 + 2) * 5000

# =========================
# MASTER BARANG
# =========================

@app.route("/barang", methods=["GET"])
def get_barang():
    cur = conn.cursor()
    cur.execute("""
        SELECT kode,nama,harga_beli,harga_jual,stok
        FROM barang
        ORDER BY nama
    """)
    rows = cur.fetchall()
    cur.close()

    data = []
    for row in rows:
        data.append({
            "kode": row[0],
            "nama": row[1],
            "harga_beli": float(row[2]),
            "harga_jual": float(row[3]),
            "stok": int(row[4])
        })

    return jsonify(data)

@app.route("/simpan_barang", methods=["POST"])
def simpan_barang():
    data = request.get_json()

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO barang
        (kode,nama,harga_beli,harga_jual,stok)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        data["kode"],
        data["nama"],
        data["hargaBeli"],
        data["hargaJual"],
        data["stok"]
    ))
    conn.commit()
    cur.close()

    return jsonify({"message":"Barang berhasil disimpan"})

# =========================
# MASTER SUPPLIER
# =========================

@app.route("/supplier", methods=["GET"])
def get_supplier():
    cur = conn.cursor()
    cur.execute("""
        SELECT nama,hp,alamat
        FROM supplier
        ORDER BY nama
    """)
    rows = cur.fetchall()
    cur.close()

    data = []
    for row in rows:
        data.append({
            "nama": row[0],
            "hp": row[1],
            "alamat": row[2]
        })

    return jsonify(data)

@app.route("/simpan_supplier", methods=["POST"])
def simpan_supplier():
    data = request.get_json()

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO supplier
        (nama,hp,alamat)
        VALUES (%s,%s,%s)
    """, (
        data["nama"],
        data["hp"],
        data["alamat"]
    ))
    conn.commit()
    cur.close()

    return jsonify({"message":"Supplier berhasil disimpan"})

# =========================
# PEMBELIAN
# =========================

@app.route("/simpan_pembelian", methods=["POST"])
def simpan_pembelian():

    data = request.get_json()

    cur = conn.cursor()

    # CEK DUPLIKAT
    cur.execute("""
        SELECT COUNT(*)
        FROM pembelian
        WHERE tanggal=%s
        AND supplier=%s
        AND barang=%s
        AND qty=%s
        AND total=%s
    """, (
        data["tanggal"],
        data["supplier"],
        data["barang"],
        data["qty"],
        data["total"]
    ))

    cek = cur.fetchone()[0]

    if cek > 0:
        cur.close()

        return jsonify({
            "message":"Pembelian sudah pernah diinput"
        })

    # Simpan pembelian
    cur.execute("""
        INSERT INTO pembelian
        (tanggal,supplier,barang,qty,harga,status,total)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["tanggal"],
        data["supplier"],
        data["barang"],
        data["qty"],
        data["harga"],
        data["status"],
        data["total"]
    ))

    # Tambah stok barang
    cur.execute("""
        UPDATE barang
        SET stok = stok + %s
        WHERE nama = %s
    """, (
        data["qty"],
        data["barang"]
    ))

    # Jika pembelian lunas otomatis kurangi kas
    if data["status"] == "LUNAS":

        cur.execute("""
            INSERT INTO kas
            (tanggal,keterangan,masuk,keluar)
            VALUES (%s,%s,%s,%s)
        """, (
            data["tanggal"],
            "PEMBELIAN BARANG",
            0,
            data["total"]
        ))

    conn.commit()
    cur.close()

    return jsonify({
        "message":"Pembelian berhasil disimpan"
    })
# =========================
# DATA PEMBELIAN
# =========================

@app.route("/pembelian", methods=["GET"])
def get_pembelian():

    cur = conn.cursor()

    cur.execute("""
        SELECT
            tanggal,
            supplier,
            barang,
            qty,
            harga,
            status,
            total
        FROM pembelian
        ORDER BY tanggal DESC
    """)

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:
        data.append({
            "tanggal": str(row[0]),
            "supplier": row[1],
            "barang": row[2],
            "qty": row[3],
            "harga": float(row[4]),
            "status": row[5],
            "total": float(row[6])
        })

    return jsonify(data)

# =========================
# INPUT HARIAN
# =========================

@app.route("/input_harian", methods=["GET"])
def get_input_harian():
    cur = conn.cursor()
    cur.execute("""
        SELECT tanggal,barang,stok_awal,sisa_stok,
               pengembalian,terjual,omzet,laba
        FROM input_harian
        ORDER BY tanggal DESC
    """)

    rows = cur.fetchall()
    cur.close()

    data = []
    for row in rows:
        data.append({
            "tanggal": str(row[0]),
            "barang": row[1],
            "stok_awal": row[2],
            "sisa_stok": row[3],
            "pengembalian": row[4],
            "terjual": row[5],
            "omzet": float(row[6]),
            "laba": float(row[7])
        })

    return jsonify(data)

@app.route("/simpan_input_harian", methods=["POST"])
def simpan_input_harian():

    data = request.get_json()

    cur = conn.cursor()

    # CEK DUPLIKAT
    cur.execute("""
        SELECT COUNT(*)
        FROM input_harian
        WHERE tanggal=%s
        AND barang=%s
    """, (
        data["tanggal"],
        data["barang"]
    ))

    cek = cur.fetchone()[0]

    if cek > 0:
        cur.close()

        return jsonify({
            "message":"Input harian barang ini sudah pernah disimpan"
        })

    # CEK STOK MINUS
    if int(data["sisa_stok"]) < 0:

        cur.close()

        return jsonify({
            "message":"Stok tidak boleh minus"
        })

    # SIMPAN INPUT HARIAN
    cur.execute("""
        INSERT INTO input_harian
        (tanggal,barang,stok_awal,tambahan,sisa_stok,
        pengembalian,terjual,harga_beli,harga_jual,
        omzet,modal,laba)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["tanggal"],
        data["barang"],
        data["stok_awal"],
        data["tambahan"],
        data["sisa_stok"],
        data["pengembalian"],
        data["terjual"],
        data["harga_beli"],
        data["harga_jual"],
        data["omzet"],
        data["modal"],
        data["laba"]
    ))

    # UPDATE STOK
    cur.execute("""
        UPDATE barang
        SET stok=%s
        WHERE nama=%s
    """, (
        data["sisa_stok"],
        data["barang"]
    ))

    conn.commit()
    cur.close()

    return jsonify({
        "message":"Input harian berhasil disimpan"
    })
    # TAMBAH KAS DARI PENJUALAN
    cur.execute("""
        INSERT INTO kas
        (
            tanggal,
            keterangan,
            masuk,
            keluar
        )
        VALUES (%s,%s,%s,%s)
    """, (
        data["tanggal"],
        "PENJUALAN - " + data["barang"],
        data["omzet"],
        0
    ))
# =========================
# LAPORAN HARIAN
# =========================

@app.route("/laporan_harian", methods=["GET"])
def laporan_harian():
    tanggal = request.args.get("tanggal")

    cur = conn.cursor()

    cur.execute("""
        SELECT barang,stok_awal,pengembalian,
               terjual,sisa_stok,omzet,modal,laba
        FROM input_harian
        WHERE tanggal=%s
    """, (tanggal,))

    rows = cur.fetchall()
    cur.close()

    data = []

    for row in rows:
        data.append({
            "barang": row[0],
            "stok_awal": row[1],
            "pengembalian": row[2],
            "terjual": row[3],
            "sisa_stok": row[4],
            "omzet": float(row[5]),
            "modal": float(row[6]),
            "laba": float(row[7])
        })

    return jsonify(data)

# =========================
# LAPORAN HUTANG
# =========================

@app.route("/laporan_hutang", methods=["GET"])
def laporan_hutang():

    cur = conn.cursor()

    cur.execute("""
        SELECT
        tanggal,
        supplier,
        barang,
        total,
        COALESCE(sudah_dibayar,0) AS sudah_dibayar,
        COALESCE(retur,0) AS retur,
        (
            total
            - COALESCE(sudah_dibayar,0)
            - COALESCE(retur,0)
        ) AS sisa_hutang
        FROM pembelian
        WHERE status='HUTANG'
AND (
    total
    - COALESCE(sudah_dibayar,0)
    - COALESCE(retur,0)
) > 0
    """)

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:
        data.append({
            "tanggal": str(row[0]),
            "supplier": row[1],
            "barang": row[2],
            "total": float(row[3]),
            "sudah_dibayar": float(row[4]),
            "retur": float(row[5]) if row[5] is not None else 0,
            "sisa_hutang": float(row[6])
    })

    return jsonify(data)
# =========================
# PEMBAYARAN SUPPLIER
# =========================

# =========================
# PEMBAYARAN SUPPLIER
# =========================

@app.route("/pembayaran_supplier", methods=["GET"])
def get_pembayaran_supplier():

    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            tanggal,
            supplier,
            nominal,
            keterangan
        FROM pembayaran_supplier
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "tanggal": str(row[1]),
            "supplier": row[2],
            "nominal": float(row[3]),
            "keterangan": row[4]
        })

    return jsonify(data)

@app.route("/simpan_pembayaran_supplier", methods=["POST"])
def simpan_pembayaran_supplier():

    data = request.get_json()

    cur = conn.cursor()

    # SIMPAN HEADER PEMBAYARAN
    cur.execute("""
        INSERT INTO pembayaran_supplier
        (
            tanggal,
            supplier,
            nominal,
            keterangan
        )
        VALUES (%s,%s,%s,%s)
        RETURNING id
    """, (
        data["tanggal"],
        data["supplier"],
        data["nominal"],
        data["keterangan"]
    ))

    pembayaran_id = cur.fetchone()[0]

    # KURANGI KAS
    cur.execute("""
        INSERT INTO kas
        (
            tanggal,
            keterangan,
            masuk,
            keluar
        )
        VALUES (%s,%s,%s,%s)
    """, (
        data["tanggal"],
        "PEMBAYARAN SUPPLIER",
        0,
        data["nominal"]
    ))

    # BAYAR HUTANG
    sisa_bayar = float(data["nominal"])

    cur.execute("""
        SELECT
            id,
            barang,
            total,
            COALESCE(sudah_dibayar,0),
            COALESCE(retur,0)
        FROM pembelian
        WHERE status='HUTANG'
        AND supplier=%s
        AND (
            total
            - COALESCE(sudah_dibayar,0)
            - COALESCE(retur,0)
        ) > 0
        ORDER BY tanggal,id
    """, (
        data["supplier"],
    ))

    hutang_list = cur.fetchall()

    print("SUPPLIER =", data["supplier"])
    print("HUTANG LIST =", hutang_list)

    for hutang in hutang_list:

        id_pembelian = hutang[0]
        barang = hutang[1]
        total = float(hutang[2])
        sudah_dibayar = float(hutang[3])
        retur = float(hutang[4])

        sisa_hutang = (
            total
            - sudah_dibayar
            - retur
        )

        if sisa_bayar <= 0:
            break

        bayar = min(
            sisa_bayar,
            sisa_hutang
        )

        # UPDATE PEMBELIAN
        cur.execute("""
            UPDATE pembelian
            SET sudah_dibayar =
                COALESCE(sudah_dibayar,0) + %s
            WHERE id=%s
        """, (
            bayar,
            id_pembelian
        ))

        # SIMPAN DETAIL PEMBAYARAN
        cur.execute("""
            INSERT INTO
            pembayaran_supplier_detail
            (
                pembayaran_id,
                pembelian_id,
                barang,
                nominal
            )
            VALUES
            (%s,%s,%s,%s)
        """, (
            pembayaran_id,
            id_pembelian,
            barang,
            bayar
        ))

        sisa_bayar -= bayar

    conn.commit()

    cur.close()

    return jsonify({
        "message": "Pembayaran supplier berhasil disimpan",
        "id": pembayaran_id
    })
    # =========================
# OPERASIONAL
# =========================

@app.route("/operasional", methods=["GET"])
def get_operasional():

    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            tanggal,
            kategori,
            keterangan,
            jumlah
        FROM operasional
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "tanggal": str(row[1]),
            "kategori": row[2],
            "keterangan": row[3],
            "jumlah": float(row[4])
        })

    return jsonify(data)


@app.route("/simpan_operasional", methods=["POST"])
def simpan_operasional():

    data = request.get_json()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO operasional
        (tanggal,kategori,keterangan,jumlah)
        VALUES (%s,%s,%s,%s)
    """, (
        data["tanggal"],
        data["kategori"],
        data["keterangan"],
        data["jumlah"]
    ))

    # otomatis masuk pengeluaran kas
    cur.execute("""
        INSERT INTO kas
        (tanggal,keterangan,masuk,keluar)
        VALUES (%s,%s,%s,%s)
    """, (
        data["tanggal"],
        "OPERASIONAL - " + data["kategori"],
        0,
        data["jumlah"]
    ))

    conn.commit()
    cur.close()

    return jsonify({
        "message":"Operasional berhasil disimpan"
    })
 # =========================
# RETUR SUPPLIER
# =========================

@app.route("/retur_supplier", methods=["GET"])
def get_retur_supplier():

    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            tanggal,
            supplier,
            barang,
            qty,
            harga_beli,
            total,
            keterangan
        FROM retur_supplier
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "tanggal": str(row[1]),
            "supplier": row[2],
            "barang": row[3],
            "qty": float(row[4]),
            "harga_beli": float(row[5]),
            "total": float(row[6]),
            "keterangan": row[7]
        })

    return jsonify(data)


@app.route("/simpan_retur_supplier", methods=["POST"])
def simpan_retur_supplier():

    try:

        data = request.get_json()

        cur = conn.cursor()

        # SIMPAN RETUR
        cur.execute("""
            INSERT INTO retur_supplier
            (
                tanggal,
                supplier,
                barang,
                qty,
                harga_beli,
                total,
                keterangan
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            data["tanggal"],
            data["supplier"],
            data["barang"],
            data["qty"],
            data["harga_beli"],
            data["total"],
            data["keterangan"]
        ))

        # KURANGI STOK
        cur.execute("""
            UPDATE barang
            SET stok = stok - %s
            WHERE nama = %s
        """, (
            data["qty"],
            data["barang"]
        ))

        # KURANGI HUTANG SUPPLIER
        sisa_retur = float(data["total"])

        cur.execute("""
            SELECT
                id,
                total,
                COALESCE(sudah_dibayar,0),
                COALESCE(retur,0)
            FROM pembelian
            WHERE supplier=%s
            AND barang=%s
            AND status='HUTANG'
            ORDER BY id
        """, (
            data["supplier"],
            data["barang"]
        ))

        hutang_list = cur.fetchall()

        for hutang in hutang_list:

            id_pembelian = hutang[0]
            total_hutang = float(hutang[1])
            sudah_dibayar = float(hutang[2])
            retur = float(hutang[3])

            sisa_hutang = (
                total_hutang
                - sudah_dibayar
                - retur
            )
            if sisa_retur <= 0:
                break

            nilai_retur = min(sisa_retur, sisa_hutang)

            cur.execute("""
                UPDATE pembelian
                SET retur = COALESCE(retur,0) + %s
                WHERE id=%s
            """, (
                nilai_retur,
                id_pembelian
            ))

            sisa_retur -= nilai_retur

        conn.commit()
        cur.close()

        return jsonify({
            "success": True,
            "message": "Retur supplier berhasil disimpan"
        })

    except Exception as e:

        conn.rollback()

        print("ERROR RETUR SUPPLIER :", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
@app.route("/data_supplier", methods=["GET"])
def data_supplier():

    cur = conn.cursor()

    cur.execute("""
        SELECT nama
        FROM supplier
        ORDER BY nama
    """)

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:
        data.append({
            "nama": row[0]
        })

    return jsonify(data)
@app.route("/data_barang", methods=["GET"])
def data_barang():

    cur = conn.cursor()

    cur.execute("""
        SELECT
            nama,
            harga_beli
        FROM barang
        ORDER BY nama
    """)

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:
        data.append({
            "nama": row[0],
            "harga_beli": float(row[1])
        })

    return jsonify(data)


    return jsonify(data)
@app.route("/info_barang/<nama>", methods=["GET"])
def info_barang(nama):

    cur = conn.cursor()

    cur.execute("""
        SELECT harga_beli
        FROM barang
        WHERE nama=%s
    """, (nama,))

    barang = cur.fetchone()

    cur.execute("""
        SELECT pengembalian
        FROM input_harian
        WHERE barang=%s
        ORDER BY id DESC
        LIMIT 1
    """, (nama,))

    pengembalian = cur.fetchone()

    cur.close()

    return jsonify({
        "harga_beli": float(barang[0]) if barang else 0,
        "pengembalian": int(pengembalian[0]) if pengembalian else 0
    })
@app.route("/pencarian", methods=["GET"])
def pencarian():

    keyword = request.args.get("keyword")

    hasil = []

    cur = conn.cursor()

    # PEMBELIAN
    cur.execute("""
        SELECT tanggal,supplier,barang,total
        FROM pembelian
        WHERE barang ILIKE %s
        OR supplier ILIKE %s
    """, (
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    for row in cur.fetchall():

        hasil.append({
            "sumber":"Pembelian",
            "keterangan":
            f"{row[0]} | {row[1]} | {row[2]} | Rp {row[3]}"
        })

    # INPUT HARIAN
    cur.execute("""
        SELECT tanggal,barang,terjual
        FROM input_harian
        WHERE barang ILIKE %s
    """, (
        f"%{keyword}%",
    ))

    for row in cur.fetchall():

        hasil.append({
            "sumber":"Input Harian",
            "keterangan":
            f"{row[0]} | {row[1]} | Terjual {row[2]}"
        })

    # PEMBAYARAN SUPPLIER
    cur.execute("""
        SELECT tanggal,supplier,nominal
        FROM pembayaran_supplier
        WHERE supplier ILIKE %s
    """, (
        f"%{keyword}%",
    ))

    for row in cur.fetchall():

        hasil.append({
            "sumber":"Pembayaran Supplier",
            "keterangan":
            f"{row[0]} | {row[1]} | Rp {row[2]}"
        })

    # OPERASIONAL
    cur.execute("""
        SELECT
            tanggal,
            kategori,
            keterangan,
            jumlah
        FROM operasional
        WHERE kategori ILIKE %s
        OR keterangan ILIKE %s
    """, (
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    for row in cur.fetchall():

        hasil.append({
            "sumber":"Operasional",
            "keterangan":
            f"{row[0]} | {row[1]} | {row[2]} | Rp {row[3]}"
        })
    # RETUR SUPPLIER
    cur.execute("""
        SELECT
            tanggal,
            supplier,
            barang,
            total
        FROM retur_supplier
        WHERE supplier ILIKE %s
        OR barang ILIKE %s
        OR keterangan ILIKE %s
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    for row in cur.fetchall():

        hasil.append({
            "sumber":"Retur Supplier",
            "keterangan":
            f"{row[0]} | {row[1]} | {row[2]} | Rp {row[3]}"
        })
    cur.close()

    return jsonify(hasil)
@app.route('/laporan')
def halaman_laporan():
    return render_template(
        'laporan_mutasi_brilink.html'
    )
@app.route('/data_mutasi_brilink')
def data_mutasi_brilink():

    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')

    cur = conn.cursor()

    cur.execute("""
        SELECT
            tanggal_transaksi,
            keterangan,
            nominal,
            admin_otomatis
        FROM mutasi_brilink
        WHERE DATE(tanggal_transaksi)
        BETWEEN %s AND %s
        ORDER BY tanggal_transaksi
    """,(tgl_awal,tgl_akhir))

    hasil = []

    for row in cur.fetchall():

        hasil.append({
            "tanggal": str(row[0]),
            "keterangan": row[1],
            "nominal": float(row[2]),
            "admin": float(row[3])
        })

    cur.close()

    return jsonify(hasil)
@app.route('/export_mutasi_brilink')
def export_mutasi_brilink():

    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')

    query = """
    SELECT
        tanggal_transaksi,
        keterangan,
        nominal,
        admin_otomatis
    FROM mutasi_brilink
    WHERE DATE(tanggal_transaksi)
    BETWEEN %s AND %s
    ORDER BY tanggal_transaksi
    """

    df = pd.read_sql(
        query,
        conn,
        params=[tgl_awal, tgl_akhir]
    )

    # Ganti nama kolom
    df.columns = [
        "Tanggal Transaksi",
        "Keterangan",
        "Nominal",
        "Admin"
    ]

    # Hitung total
    total_nominal = df["Nominal"].sum()
    total_admin = df["Admin"].sum()

    # Format rupiah
    df["Nominal"] = df["Nominal"].apply(
        lambda x: f"Rp {x:,.0f}".replace(",", ".")
    )

    df["Admin"] = df["Admin"].apply(
        lambda x: f"Rp {x:,.0f}".replace(",", ".")
    )

    # Tambah baris total
    df.loc[len(df)] = [
        "",
        "TOTAL",
        f"Rp {total_nominal:,.0f}".replace(",", "."),
        f"Rp {total_admin:,.0f}".replace(",", ".")
    ]

    # Nama file pakai tanggal
    nama_file = (
        f"Laporan_TF_{tgl_awal}_sd_{tgl_akhir}.xlsx"
    )

    # Simpan Excel
    df.to_excel(
        nama_file,
        index=False
    )

    # Atur lebar kolom
    wb = load_workbook(nama_file)
    ws = wb.active

    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 80
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 20

    wb.save(nama_file)

    return send_file(
        nama_file,
        as_attachment=True
    )
# =========================
# DASHBOARD
# =========================

@app.route("/dashboard", methods=["GET"])
def dashboard():
    cur = conn.cursor()

    # Omzet
    cur.execute("""
        SELECT COALESCE(SUM(omzet),0)
        FROM input_harian
    """)
    omzet = cur.fetchone()[0]

    # Laba
    cur.execute("""
        SELECT COALESCE(SUM(laba),0)
        FROM input_harian
    """)
    laba = cur.fetchone()[0]

    # Saldo Kas
    cur.execute("""
        SELECT
            COALESCE(SUM(masuk),0)
            -
            COALESCE(SUM(keluar),0)
        FROM kas
    """)
    saldo_kas = cur.fetchone()[0]

    # Hutang Supplier
    cur.execute("""
    SELECT COALESCE(
        SUM(
            total
            - COALESCE(sudah_dibayar,0)
            - COALESCE(retur,0)
        ),
    0)
    FROM pembelian
    WHERE status='HUTANG'
    """)
    hutang = cur.fetchone()[0]

    # Persediaan
    cur.execute("""
    SELECT COALESCE(SUM(stok * harga_beli),0)
    FROM barang
     """)
    persediaan = cur.fetchone()[0]

    # Stok Menipis
    cur.execute("""
    SELECT nama, stok
    FROM barang
    """)
    data_barang = cur.fetchall()

    barang_menipis = []

    for nama_barang, stok in data_barang:

        if "mie" in nama_barang.lower():
            if stok <= 7:
                barang_menipis.append(
                    f"{nama_barang} ({stok})"
                )

        else:
            if stok <= 15:
                barang_menipis.append(
                    f"{nama_barang} ({stok})"
                )

    stok_menipis = len(barang_menipis)

    daftar_stok_menipis = "<br>".join(
        barang_menipis
    )

    # Aset
    aset_kotor = saldo_kas + persediaan
    aset_bersih = aset_kotor - hutang 

    cur.close()

    return jsonify({
        "omzet": float(omzet),
        "laba": float(laba),
        "saldo_kas": float(saldo_kas),
        "hutang_supplier": float(hutang),
        "persediaan": float(persediaan),
        "aset_kotor": float(aset_kotor),
        "aset_bersih": float(aset_bersih),
        "stok_menipis": stok_menipis,
        "daftar_stok_menipis": daftar_stok_menipis
    })


@app.route("/login_qlola")
def login_qlola():
    return redirect("https://qlola.bri.co.id")

@app.route("/auto_mutasi")
def auto_mutasi():

    try:

        folder_download = r"C:\Users\kapib\Downloads"

        daftar_csv = glob.glob(
            os.path.join(folder_download, "*.csv")
        )

        if not daftar_csv:
            return jsonify({
                "status": "error",
                "pesan": "Tidak ada file CSV di folder Downloads"
            })

        file_terbaru = max(
            daftar_csv,
            key=os.path.getctime
        )

        df = pd.read_csv(file_terbaru)

        cur = conn.cursor()

        jumlah_import = 0

        for _, row in df.iterrows():

            nominal = pd.to_numeric(
                row.get("MUTASI_KREDIT", 0),
                errors="coerce"
            )

            if pd.isna(nominal):
                continue

            nominal = float(nominal)

            if nominal <= 0:
                continue

            tanggal_text = str(
                row.get("TGL_TRAN", "")
            ).strip()

            try:

                tanggal_jam = datetime.strptime(
                    tanggal_text,
                    "%Y-%m-%d %H:%M:%S"
                )

            except:

                continue

            keterangan = str(
                row.get("REMARK_CUSTOM", "")
            ).strip()

            admin_otomatis = hitung_admin(
                nominal
            )
            cur.execute("""
                SELECT id
                FROM mutasi_brilink
                WHERE tanggal_transaksi = %s
                AND nominal = %s
            """, (tanggal_jam, nominal))

            sudah_ada = cur.fetchone()

            if sudah_ada:
                continue
            cur.execute("""
                INSERT INTO mutasi_brilink
                (
                    tanggal_transaksi,
                    nominal,
                    keterangan,
                    admin_otomatis
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT
                (
                    tanggal_transaksi,
                    nominal,
                    keterangan
                )
                DO NOTHING
            """, (
                tanggal_jam,
                nominal,
                keterangan,
                admin_otomatis
            ))

            if cur.rowcount > 0:
                jumlah_import += 1

        conn.commit()
        cur.close()

        if jumlah_import == 0:

            return jsonify({
                "status": "warning",
                "pesan": "Tidak ada data baru untuk diimport",
                "file": os.path.basename(file_terbaru)
            })

        return jsonify({
            "status": "success",
            "pesan": f"Berhasil import {jumlah_import} transaksi",
            "file": os.path.basename(file_terbaru),
            "jumlah_import": jumlah_import
        })

    except Exception as e:

        conn.rollback()

        return jsonify({
            "status": "error",
            "pesan": str(e)
        })
@app.route("/data_laporan_tarik_tunai")
def data_laporan_tarik_tunai():

    tanggal = request.args.get("tanggal")

    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            tanggal_transaksi,
            keterangan,
            nominal,
            admin_otomatis,
            sudah_diproses,
            waktu_proses
        FROM mutasi_brilink
        WHERE DATE(tanggal_transaksi) = %s
        ORDER BY tanggal_transaksi
    """, (tanggal,))

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:

        data.append({
            "id": row[0],
            "tanggal": str(row[1]),
            "bank": row[2],
            "nominal": float(row[3]),
            "admin": float(row[4]),
            "sudah_diproses": row[5],
            "waktu_proses": str(row[6]) if row[6] else "",
            "uang_diserahkan":
                float(row[3]) - float(row[4])
        })

    return jsonify(data)
@app.route("/update_tarik_tunai", methods=["POST"])
def update_tarik_tunai():

    data = request.get_json()

    cur = conn.cursor()

    if data["status"]:

        cur.execute("""
            UPDATE mutasi_brilink
            SET
                sudah_diproses = TRUE,
                waktu_proses = NOW()
            WHERE id = %s
        """, (
            data["id"],
        ))

    else:

        cur.execute("""
            UPDATE mutasi_brilink
            SET
                sudah_diproses = FALSE,
                waktu_proses = NULL
            WHERE id = %s
        """, (
            data["id"],
        ))

    conn.commit()
    cur.close()

    return jsonify({
        "status": "success"
    })
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data["username"]
    password = data["password"]

    cur = conn.cursor()

    cur.execute("""
        SELECT role
        FROM users
        WHERE username=%s
        AND password=%s
    """, (username, password))

    user = cur.fetchone()

    cur.close()

    if user:

        session["user"] = username
        session["role"] = user[0]

        return jsonify({
            "status": "success",
            "role": user[0]
        })

    return jsonify({
        "status": "error",
        "message": "Username atau Password salah"
    })
@app.route("/cek_login")
def cek_login():

    if "user" not in session:

        return jsonify({
            "login": False
        })

    return jsonify({
        "login": True,
        "user": session["user"],
        "role": session["role"]
    })
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login.html")

@app.route("/login.html")
def halaman_login():

    return send_from_directory(
        ".",
        "login.html"
    )
@app.route("/hutang_supplier/<supplier>", methods=["GET"])
def hutang_supplier(supplier):

    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            barang,
            total,
            COALESCE(sudah_dibayar,0),
            COALESCE(retur,0),
            (
                total
                - COALESCE(sudah_dibayar,0)
                - COALESCE(retur,0)
            ) AS sisa_hutang
        FROM pembelian
        WHERE supplier=%s
        AND status='HUTANG'
        AND (
            total
            - COALESCE(sudah_dibayar,0)
            - COALESCE(retur,0)
        ) > 0
        ORDER BY id
    """, (supplier,))

    rows = cur.fetchall()

    cur.close()

    data = []

    for row in rows:

        data.append({
            "id": row[0],
            "barang": row[1],
            "total": float(row[2]),
            "sudah_dibayar": float(row[3]),
            "retur": float(row[4]),
            "sisa_hutang": float(row[5])
        })

    return jsonify(data)
@app.route("/cetak_pembayaran_supplier/<int:pembayaran_id>")
def cetak_pembayaran_supplier(pembayaran_id):

    cur = conn.cursor()

    cur.execute("""
        SELECT
            tanggal,
            supplier,
            nominal,
            COALESCE(keterangan,'')
        FROM pembayaran_supplier
        WHERE id=%s
    """, (pembayaran_id,))

    pembayaran = cur.fetchone()

    if not pembayaran:

        cur.close()

        return "Data tidak ditemukan"

    tanggal = pembayaran[0]
    supplier = pembayaran[1]
    total = pembayaran[2]
    keterangan = pembayaran[3]

    cur.execute("""
        SELECT
            barang,
            nominal
        FROM pembayaran_supplier_detail
        WHERE pembayaran_id=%s
    """, (pembayaran_id,))

    detail = cur.fetchall()

    cur.close()

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("D'ELBAR KANTIN", styles["Title"])
    )

    elements.append(
        Paragraph(
            "BUKTI PEMBAYARAN SUPPLIER",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1,12))

    elements.append(
        Paragraph(
            f"Tanggal : {tanggal}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Supplier : {supplier}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1,12))

    elements.append(
        Paragraph(
            "Barang Yang Dibayar",
            styles["Heading3"]
        )
    )

    for item in detail:

        barang = item[0]
        nominal = float(item[1])

        elements.append(
            Paragraph(
                f"{barang} - Rp {nominal:,.0f}",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1,12))

    elements.append(
        Paragraph(
            f"TOTAL PEMBAYARAN : Rp {float(total):,.0f}",
            styles["Heading3"]
        )
    )

    elements.append(Spacer(1,12))

    elements.append(
        Paragraph(
            f"Keterangan : {keterangan}",
            styles["Normal"]
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=False,
        download_name=
        f"Pembayaran_{supplier}.pdf",
        mimetype="application/pdf"
    )
if __name__ == "__main__":
    app.run(debug=True)