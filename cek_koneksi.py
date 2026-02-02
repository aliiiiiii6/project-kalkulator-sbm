import google.generativeai as genai

# GANTI DENGAN API KEY KAMU
genai.configure(api_key="AIzaSyAwPBQgf-pg0H9fw0TDdnTuOLfhDVed4Bg")

print("--- Mengecek Daftar Model yang Tersedia ---")
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models:
        for model in available_models:
            print(f"✅ Tersedia: {model}")
    else:
        print("❌ Tidak ada model yang ditemukan untuk API Key ini.")
except Exception as e:
    print(f"❌ Error saat list models: {e}")