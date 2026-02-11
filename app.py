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
# INIT SESSION CHAT HISTORY
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# 3. UI
# ==============================
# ==============================
# GPT-LIKE CLEAN UI STYLE
# ==============================
st.markdown("""
<style>

/* ===== ROOT APP ===== */
html, body, .stApp {
    background: radial-gradient(circle at 50% -10%, #dfe6ff 0%, #f5f7ff 35%, #ffffff 75%) !important;
}

/* ===== STREAMLIT WHITE LAYERS (INI BIANGNYA) ===== */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
section.main,
section.main > div {
    background: transparent !important;
}

/* container tengah */
.block-container{
    max-width: 900px;
    padding-top: 2rem;
    background: transparent !important;
}

/* HERO */
.gpt-hero{
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(12px);
    border-radius:20px;
    padding:30px;
    box-shadow:0 10px 30px rgba(0,0,0,0.06);
    text-align:center;
    margin-bottom:25px;
}
/* ===== CHAT WIDTH FIX ===== */
[data-testid="stChatMessage"] {
    max-width: 50%;
}

/* assistant kiri */
[data-testid="stChatMessage"]:has([data-testid="stMarkdownContainer"]) {
    margin-left: 1px;
}

/* user kanan */
[data-testid="stChatMessage"]:has(.stChatMessageAvatarUser) {
    margin-right: 2px;
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
# TAMPILKAN CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Masukan Segala Informasi Yang Kamu Butuhkan")

# ==============================
# 4. LOGIC AI
# ==============================
# ==============================
# 4. LOGIC AI
# ==============================
if user_input:

    # simpan pesan user
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # tampilkan bubble user
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("sebentar yaaa, Arin lagi ngetik nih..."):

        context = get_excel_context(user_input)

        history_text = ""
        for m in st.session_state.messages:
            history_text += f"{m['role'].upper()} : {m['content']}\n"

        prompt = f"""
Kamu adalah sistem analis anggaran instansi pemerintah.

Riwayat Percakapan:
{history_text}

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

### Ringkasan Anggaran
| Item | Nilai |
|------|------|

### Kesimpulan

Pertanyaan User:
{user_input}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        ai_reply = response.text

    # tampilkan bubble assistant
    with st.chat_message("assistant"):
        st.markdown(ai_reply)

    # simpan history assistant
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_reply
    })

