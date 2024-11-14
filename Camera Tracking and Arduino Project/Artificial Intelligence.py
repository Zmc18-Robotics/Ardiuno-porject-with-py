import openai

# Ganti dengan API Key Anda
openai.api_key = '-'

# Menggunakan model GPT-3.5 Turbo atau GPT-4 untuk chat
response = openai.chat.completions.create(
    model="gpt-3.5-turbo",  # Model percakapan
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how can I use OpenAI API?"}
    ]
)

print(response['choices'][0]['message']['content'])
