import google.generativeai as genai

genai.configure(api_key="AIzaSyAwPBQgf-pg0H9fw0TDdnTuOLfhDVed4Bg")

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)