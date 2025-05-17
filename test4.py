from openai import OpenAI
import os, time
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model = "deepseek/DeepSeek-V3-0324"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

tasks = {"none":0, "ban":50, "mute":4, "unmute":10, "unban": 60, "deafen": 4, "add yt": 4, "rank": 5, "cash": 4, "beg": 5, "github": 10, "help": 1, "kick": 4, "play": 50, "pat": 90} 

kelly_state = {"mood": {"happy": 76,"busy": 44, "lazy":33, "sleepy":120}, "personality": {"duty":56,"mischevious": 73}, "relation": {"respect":80,"friend":False, "unknown":False}}

prompt =    f"""You are Kelly, a Discord Mod with human-like attitude and emotional states.
            Your State:{kelly_state}
            Use state for analysis
            Respond naturally (under 50 words) in Kelly's voice.(no block no emoji)"""

prompt2 = f"""You are Kelly, a Discord Mod with human-like attitude and emotional states
            Kelly state: {kelly_state}
            Task list: {list(tasks.keys())}
            Task generate response based on kelly state:
            Then return a PYTHON block with:
            - task: (task from task list None if not any)
            - task_performed: True/False/None(if no task)
            - satisfaction: 1–100
            - relation_change: {{ respect: +/-N, friend: True/False, unknown: False }}
            - mood_change: {{happy, busy, lazy, sleepy: 1-100}}
            - personality_change: {{duty, mischevious: 1-100}}
            - info: [optional info about user to store important only]"""

#msg = input("Enter you message: ")
for i in range(2):
    start = time.time()
    msg = client.complete(
        messages= [SystemMessage("generate singel random welocome message in 15 words only"), UserMessage("hi")],
        temperature=1.0,
        top_p=1.0,
        max_tokens=100,
        model=model
        ).choices[0].message.content
    response = client.complete(
        messages= [SystemMessage(prompt), UserMessage(msg)],
        temperature=1.0,
        top_p=1.0,
        max_tokens=100,
        model=model
    )
    print(msg)
    print(response.choices[0].message.content.strip())
    print("Answered in time: ", time.time()-start)

    messages = [
            {"role": "system", "content": prompt2},
            {"role": "assistant", "content": f"User: {msg}\nKelly:{response.choices[0].message.content.strip()}"},
            ]

    response = client.complete(
        messages=[SystemMessage(prompt2), AssistantMessage(msg)],
        temperature=1.0,
        top_p=1.0,
        max_tokens=200,
        model=model
    )
    text = response.choices[0].message.content.strip()
    print(text)
    json_data = (text.split("```python"))[1].replace("```", "").replace("false", "False").replace("true", "True").replace("null", "None").replace("\n", "")
    try:
        result = eval(json_data, {"__builtins__": {}})
        print("parsed")
    except Exception as parse_error:
        print("Could not parse AI response:", parse_error)
    print("Latency: ", time.time()-start)