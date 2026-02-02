import streamlit as st
import pandas as pd
from google import genai # Library baru sesuai anjuran terminal lu

# --- 1. SETUP CLIENT ---
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)


st.set_page_config(page_title="PUSBIN AI 2026", layout="wide")

# --- 2. FUNGSI LOAD DATA ---
def get_excel_context():
    file_path = "Database_Kantor.xlsx"
    all_data = ""
    xl = pd.ExcelFile(file_path)
    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        all_data += f"\n[SHEET: {sheet}]\n{df.to_string(index=False)}\n"
    return all_data

# --- 3. UI & LOGIC ---
st.title("🤖 PUSBIN Smart Assistant (Arin)")

user_input = st.text_input("Ketik rencana kegiatan atau cek anggaran:")

if user_input:
    with st.spinner("Arin sedang menganalisis..."):
        context = get_excel_context()
        
        # Perintah ke Arin
        response = client.models.generate_content(
            model="models/gemini-2.5-flash", # Pakai model yang tersedia di akun lu
            contents=f"Data Excel: {context}\n\nUser: {user_input}\n\nJawab dengan detail sisa anggaran dan hitungan SBM."
        )
        
        st.markdown(response.text)
