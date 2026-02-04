pasti ada lagi : import streamlit as st
import pandas as pd
from google import genai
import re
import json
def clean_number(val):
    if pd.isna(val):
        return 0
    val = str(val)
    val = val.replace(".", "").replace(",", ".")
    try:
        return float(val)
    except:
        return 0

# ==============================
# 1. SETUP CLIENT GEMINI
# ==============================
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="PUSBIN AI 2026", layout="wide")

# ==============================
# 2. LOAD & FORMAT EXCEL CONTEXT
# ==============================
@st.cache_data
def get_column_structure():
    file_path = "Database_Kantor.xlsx"
    xl = pd.ExcelFile(file_path)

    struktur = ""

    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, nrows=1)
        struktur += f"\nSheet {sheet}: {list(df.columns)}"

    return struktur

      @st.cache_data
def get_excel_context(query):
    file_path = "Database_Kantor.xlsx"
    xl = pd.ExcelFile(file_path)
    query = query.lower()
    keywords = query.split()

    summary = ""

    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        df = df.dropna(axis=1, how="all")

        mask = df.astype(str).apply(
            lambda row: any(
                kw in " ".join(row.values.astype(str)).lower()
                for kw in keywords
            ),
            axis=1,
        )

        filtered = df[mask]

        if filtered.empty:
            filtered = df.head(3)

        summary += f"\n=== SHEET: {sheet} ===\n{filtered.to_csv(index=False)}\n"

    return summary

def execute_calculation(kolom_list):
    file_path = "Database_Kantor.xlsx"
    xl = pd.ExcelFile(file_path)

    total = 0

    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        df = df.dropna(axis=1, how="all")

        for kol in kolom_list:
            if kol in df.columns:
                df[kol] = df[kol].apply(clean_number)
                total += df[kol].sum()

    return total

# ==============================
# 3. UI
# ==============================
st.title("🤖 PUSBIN Smart Assistant (Arin)")

user_input = st.text_input("Ketik rencana kegiatan atau cek anggaran:")

# ==============================
# 4. LOGIC AI
# ==============================
# ==============================
# 4. LOGIC AI (1 CALL VERSION)
# ==============================
if user_input:

    with st.spinner("Arin sedang menganalisis..."):

        context = get_excel_context(user_input)
        struktur_kolom = get_column_structure()

        master_prompt = f"""
Kamu adalah sistem analis anggaran instansi pemerintah.

STRUKTUR KOLOM EXCEL:
{struktur_kolom}

CONTEXT DATA:
{context}

Tugas:
1. Tentukan kolom mana yang perlu dihitung
2. Jelaskan analisis secara singkat

Balas dalam JSON SAJA:

{{
  "kolom": ["nama_kolom"],
  "analisis_awal": "penjelasan singkat"
}}

Pertanyaan User:
{user_input}
"""

        response = client.models.generate_content(
            model="gemini-3.0-flash",
            contents=master_prompt
        )

        try:
            hasil_json = json.loads(response.text)
            kolom_dipilih = hasil_json.get("kolom", [])
            analisis_awal = hasil_json.get("analisis_awal", "")
        except:
            kolom_dipilih = []
            analisis_awal = "Model gagal menentukan kolom."

        # ======================
        # PANDAS HITUNG
        # ======================
        hasil_hitung = execute_calculation(kolom_dipilih)

        # ======================
        # OUTPUT FINAL (NO SECOND CALL)
        # ======================
        final_text = f"""
### 1. Analisis
{analisis_awal}

### 2. Perhitungan
Total hasil perhitungan sistem: **Rp {hasil_hitung:,.0f}**

### 3. Kesimpulan
Perhitungan dilakukan menggunakan data numerik dari Excel secara langsung.
"""

        st.markdown(final_text)
