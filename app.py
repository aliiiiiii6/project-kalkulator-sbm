import streamlit as st
import pandas as pd
from google import genai

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
def get_excel_context(query):
    file_path = "Database_Kantor.xlsx"
    summary = ""

    xl = pd.ExcelFile(file_path)
    query = query.lower()

    keywords = query.split()

    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        df = df.dropna(axis=1, how="all")

        mask = df.astype(str).apply(
            lambda row: any(
                kw.lower() in " ".join(row.values.astype(str)).lower()
                for kw in keywords
            ),
            axis=1,
        )

        filtered = df[mask]

        # fallback kalau kosong
        if filtered.empty:
            filtered = df.head(5)

        summary += f"\n=== SHEET: {sheet} ===\n{filtered.to_csv(index=False)}\n"

    return summary

# ==============================
# 3. UI
# ==============================
st.title("🤖 PUSBIN Smart Assistant (Arin)")

user_input = st.text_input("Ketik rencana kegiatan atau cek anggaran:")

# ==============================
# 4. LOGIC AI
# ==============================
if user_input:

    with st.spinner("sebentar yaaa, Arin lagi ngetik nih..."):

        context = get_excel_context(user_input)

        prompt = f"""
Kamu adalah sistem analis anggaran instansi pemerintah.

Gunakan data berikut sebagai database:
{context}

Instruksi:
- Identifikasi komponen biaya dari pertanyaan user
- Cocokkan dengan data SBM pada Excel
- Hitung sisa anggaran jika ada
- Gunakan HANYA data numerik yang muncul dalam tabel context.
Jangan membuat asumsi tarif jika data ada.
- Fokus pada perhitungan, bukan jawaban umum

Pertanyaan User:
{user_input}

Jawab dalam format:

1. Analisis
2. Perhitungan
3. Kesimpulan
"""

        response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)


        st.markdown(response.text)
