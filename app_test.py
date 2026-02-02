import streamlit as st
import pandas as pd

EXCEL_FILE = "Database_Kantor.xlsx"

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return {
        "uh_dn": pd.read_excel(EXCEL_FILE, sheet_name="Uang Harian DN"),
        "hotel": pd.read_excel(EXCEL_FILE, sheet_name="Hotel"),
        "pesawat": pd.read_excel(EXCEL_FILE, sheet_name="Pesawat"),
    }

data = load_data()
st.write("Kolom sheet Pesawat:", data["pesawat"].columns.tolist())

# -----------------------------
# PARSER INPUT
# -----------------------------
def parse_input(text):
    parts = text.lower().split()

    if len(parts) < 4 or parts[0] != "dn":
        raise ValueError("Format salah. Contoh: dn padang 3 2 hotel pesawat")

    kota = parts[1]
    hari = int(parts[2])
    orang = int(parts[3])
    komponen = parts[4:]

    return kota, hari, orang, komponen

# -----------------------------
# CARI PROVINSI DARI SHEET PESAWAT
# -----------------------------
def get_provinsi(kota, df_pesawat):
    row = df_pesawat[
        df_pesawat["Kota Tujuan"].str.lower() == kota
    ]

    if row.empty:
        raise ValueError("Kota tidak ditemukan di data pesawat")

    return row.iloc[0]["Provinsi Tujuan"]

# -----------------------------
# AMBIL TARIF
# -----------------------------
def get_tarif(df, provinsi):
    row = df[df["Provinsi"] == provinsi]
    if row.empty:
        raise ValueError(f"Tarif tidak ditemukan untuk provinsi {provinsi}")
    return row.iloc[0]["Tarif"]

# -----------------------------
# HITUNG ANGGARAN
# -----------------------------
def hitung_anggaran(text):
    kota, hari, orang, komponen = parse_input(text)
    provinsi = get_provinsi(kota, data["pesawat"])

    total = 0
    rincian = []

    if "hotel" in komponen:
        hotel = get_tarif(data["hotel"], provinsi)
        biaya = hotel * hari * orang
        total += biaya
        rincian.append(f"Hotel: Rp{biaya:,.0f}")

    uh_dn = get_tarif(data["uh_dn"], provinsi)
    biaya_uh = uh_dn * hari * orang
    total += biaya_uh
    rincian.append(f"Uang Harian DN: Rp{biaya_uh:,.0f}")

    if "pesawat" in komponen:
        row = data["pesawat"][
            data["pesawat"]["Kota Tujuan"].str.lower() == kota
        ]
        tiket = row.iloc[0]["Harga Tiket"]
        biaya = tiket * orang
        total += biaya
        rincian.append(f"Pesawat: Rp{biaya:,.0f}")

    return provinsi, total, rincian

# -----------------------------
# STREAMLIT UI MINIMAL
# -----------------------------
st.title("Kalkulator Anggaran DN (Deterministic)")

text = st.text_input("Masukkan kebutuhan (contoh: dn padang 3 2 hotel pesawat)")

if text:
    try:
        provinsi, total, rincian = hitung_anggaran(text)

        st.success(f"Provinsi tujuan: {provinsi}")
        st.markdown("### Rincian Biaya")
        for r in rincian:
            st.write("- ", r)

        st.markdown(f"## TOTAL: Rp{total:,.0f}")

        st.caption(
            "Perhitungan berbasis data Excel (SBM). "
            "Sistem deterministic, tanpa AI generatif."
        )

    except Exception as e:
        st.error(str(e))
