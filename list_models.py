import google.generativeai as genai
import os

API_KEY = "AIzaSyDQNsJuVruZKFzF0jX2Hw4786Gy9KGbpx0"
genai.configure(api_key=API_KEY)

print("Listando modelos disponíveis...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Erro ao listar modelos: {e}")
