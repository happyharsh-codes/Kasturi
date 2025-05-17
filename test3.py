import ollama, time

input("Enter a key to start:")
start = time.time()
response = ollama.chat(
    model='openchat',
    messages=[
        {'role': 'system', 'content': 'You are Kelly, a moody Discord bot.'},
        {'role': 'user', 'content': 'Can you ban someone for me?'}
    ]
)

print(response['message']['content'])
print("Latency: ", time.time()-start)
