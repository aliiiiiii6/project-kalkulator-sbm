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
            
        filtered = filtered.drop(columns=["No"], errors="ignore")
        summary += f"\n[DATA]\n{filtered.to_csv(index=False)}\n"

    return summary

# ==============================
# 3. UI
# ==============================
# ==============================
# GPT-LIKE CLEAN UI STYLE
# ==============================
st.markdown("""
<style>

/* ===== FIX BACKGROUND STREAMLIT LAYER ===== */
html, body, [data-testid="stAppViewContainer"]{
    background: radial-gradient(circle at 50% -20%, #e0e7ff 0%, #f8fafc 45%, #ffffff 80%);
}

.main {
    background: transparent !important;
}

.block-container{
    max-width: 900px;
    padding-top: 2rem;
    background: transparent !important;
}

/* ===== HERO STYLE (punya kamu) ===== */
.gpt-hero{
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(12px);
    border-radius:20px;
    padding:30px;
    box-shadow:0 10px 30px rgba(0,0,0,0.06);
    text-align:center;
    margin-bottom:25px;
}

.gpt-title{
    font-size:36px;
    font-weight:700;
    letter-spacing:-0.5px;
}

.gpt-sub{
    color:#6b7280;
    margin-top:8px;
    font-size:15px;
}

.badge-wrap{
    margin-top:18px;
}

.badge{
    display:inline-block;
    padding:6px 12px;
    margin:4px;
    border-radius:999px;
    background:#f1f5f9;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HERO SECTION (GPT STYLE)
# ==============================
st.markdown("""
<div style="
background:rgba(255,255,255,0.75);
backdrop-filter:blur(10px);
padding:30px;
border-radius:18px;
box-shadow:0 10px 25px rgba(0,0,0,0.05);
text-align:center;
">

<h1 style="margin-bottom:5px;">🤖 PUSBIN Smart Assistant (Arin)</h1>

<p style="color:#6b7280;font-size:15px;">
Asisten analisis anggaran berbasis AI yang membantu membaca data,
menghitung otomatis, dan menyusun tabel perhitungan dengan cepat.
</p>

<p>
<span style="background:#f1f5f9;padding:6px 12px;border-radius:999px;margin:4px;">📊 Analisis Anggaran</span>
<span style="background:#f1f5f9;padding:6px 12px;border-radius:999px;margin:4px;">🧮 Perhitungan Otomatis</span>
<span style="background:#f1f5f9;padding:6px 12px;border-radius:999px;margin:4px;">⚡ AI Assistant</span>
</p>

</div>
""", unsafe_allow_html=True)

st.caption("💡 Coba tanya: Hitung biaya perjalanan dinas luar kota 3 orang")

user_input = st.text_input("Masukan Segala Informasi Yang Kamu Butuhkan")

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
- Output WAJIB menggunakan tabel markdown

Format output:

### Tabel Perhitungan
| Komponen | Tarif | Volume | Total |
|----------|-------|--------|-------|
| ... | ... | ... | ... |

### Ringkasan Anggaran
| Item | Nilai |
|------|------|
| Total Biaya | ... |
| Sisa Anggaran | ... |

### Kesimpulan
Tuliskan singkat saja.

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
