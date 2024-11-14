import requests
import json

# Ganti dengan API Key yang Anda dapatkan dari Google Cloud
API_KEY = 'your-api-key'

# URL endpoint API Gemini (harus sesuai dengan dokumentasi API Google)
url = 'https://gemini.googleapis.com/v1beta/generateMessage'  # Ganti sesuai dengan endpoint yang benar

# Fungsi untuk mengirim permintaan ke API Gemini
def chat_with_gemini(user_input):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    # Payload yang dikirim ke API, berisi pesan dari pengguna
    data = {
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    # Melakukan request ke API Gemini
    response = requests.post(url, headers=headers, json=data)
    
    # Mengambil dan mengembalikan hasil response dari Gemini
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']  # Sesuaikan berdasarkan struktur response API
    else:
        return "Ada masalah dengan API. Silakan coba lagi nanti."

# Menjalankan chatbot sederhana
def run_chatbot():
    print("Chatbot siap. Ketik 'exit' untuk keluar.")
    while True:
        user_input = input("Anda: ")
        if user_input.lower() == 'exit':
            print("Chatbot selesai.")
            break
        response = chat_with_gemini(user_input)
        print(f"Chatbot: {response}")

# Mulai chatbot
run_chatbot()
