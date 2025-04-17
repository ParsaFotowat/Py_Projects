import openai

openai.api_key = 'your-api-key-here'

def summarize(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the text in bullet points."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

text = input("Paste text: ")
print(summarize(text))
