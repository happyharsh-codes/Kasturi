from together import Together
import time
from dotenv import load_dotenv
load_dotenv()


CLIENT3 = Together(api_key="d5a12e8dec01abb398f36e1473341d034930df11c31265c0d1861c8568d3e884")


prompt= """You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                Generate Json dict using kelly response and mood
                - task: (task detected from convo/ null)
                - task_performed: True/False/None(if no task)(based on mood and task difficulty)
                - respect: +/- (int)
                - mood_change: +/- (int)
                - personality_change: +/- (int)
                - info: [optional info about user to store important only]
                reply without think block"""
messages= [
    {"role": "system", "content": prompt},
    {"role": "user", "content": input("> ")}
]
start = time.time()

model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
response = CLIENT3.chat.completions.create(
    model=model,
    messages= messages)

print(response.choices[0].message.content)
print("Latency: ", (time.time()- start))