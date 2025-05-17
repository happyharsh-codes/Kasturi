import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
import time


endpoint = ""
model = "deepseek/DeepSeek-V3-0324"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)
tasks = {"none":0, "ban":50, "mute":4, "unmute":10, "unban": 60, "deafen": 4, "add yt": 4, "rank": 5, "cash": 4, "beg": 5, "github": 10, "help": 1, "kick": 4, "play": 50, "pat": 90} 
prompt = SystemMessage(
            f"""You are Kelly, a Discord Mod with human-like attitude and emotional states.
            Current State:{{"mood": {{"happy": 76,"busy": 44, "lazy":33, "sleepy":12}}, "personality": {{"duty":56,"mischevious": 73}}, "relation": {{"respect":80,"friend":False, "unknown":False}}}}
            Task list: {tasks}
            Task:
            1. Respond naturally (under 50 words) in Kelly's voice.(no emoji)
            2. Then return a PYTHON block with:
            - task_performed: True/False/None(if no task)
            - satisfaction: 1–100
            - relation_change: {{ respect: +/-N, friend: True/False, unknown: False }}
            - mood_change: {{"happy": 70 }}
            - info: [optional info about user to store important only]

            Separate the response and JSON clearly.""")
prompt2 = SystemMessage(f"""You are task (from list {list(tasks.keys())}) and tone finder. Response MUST be PYTHON like -> {{'task': 'none', 'user_tone': 'asked/told/ordered/requested'}}""")



message = input("Enter your message: ")
quote_time = time.time()
response = client.complete(
    messages=[
        prompt,
        UserMessage(message),
        AssistantMessage("")
    ],
    temperature=1.0,
    top_p=1.0,
    max_tokens=200,
    model=model
)
print(response.choices[0].message.content)
python = ((response.choices[0].message.content.split("```python"))[1]).replace("```", "").replace("false","False").replace("true", "True").replace("null", "None")
python = eval(python, {"__builtins__":{}})
# task = python["task_performed"]
print(python)
# response = client.complete(
#     messages=[
#         prompt,
#         UserMessage(f"Task:{task} (difficulty:{tasks[task]}),message: {message}"),
#         AssistantMessage("")
#     ],
#     temperature=1.0,
#     top_p=1.0,
#     max_tokens=100,
#     model=model
# )
# reply = response.choices[0].message.content
# print(reply)
print("Latency: ", time.time()-quote_time)
# json = (reply.split("```python"))[1]
# json = json.replace("```", "").replace("false","False").replace("true", "True").replace("null", "None")
# print(eval(json, {"__builtins__":{}}))

