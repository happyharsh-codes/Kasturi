import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
import time


endpoint = "https://models.github.ai/inference"
model = "deepseek/DeepSeek-V3-0324"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

'''SystemMessage(
            """You are Kelly, a Discord Mod with human-like attitude and emotional states.
            Current State:{{"mood": {"happy": 76,"busy": 44, "lazy":33, "sleepy":12}, "personality": {"duty":56,"mischevious": 73}, "relation": {"respect":80,"friend":False, "unknown":False}}}
            Task:
            Task:
            1. Respond naturally (under 50 words) in Kelly's voice.(no emoji)
            2. Then return a JSON block with:
            - task_performed: True/False
            - satisfaction: 1–100
            - relation_change: {{ respect: +/-N, friend: True/False, unknown: False }}
            - mood_change: {{ only the moods that changed, like "happy": 70 }}
            - info: [optional info about user to store important only]

            Separate the response and JSON clearly."""),'''

input("Enter any key to get your answer: ")
quote_time = time.time()
response = client.complete(
    messages=[
        SystemMessage("you are json maker. Scan the convo to find the required attributes for the given task\nTask: 'ban' arguments: ['user', 'reason']"),
        UserMessage(""),
        AssistantMessage("User: Kelly hey can you umm ban this guy for me?\nKelly: Uh, no? You gotta give me a reason first. I'm not just gonna ban someone because you said so.\nUser: uhh he is @makichan he is been spamming non stop\nKelly:*sips coffee*\nUser:Come on kelly is urgent ban him now\nKelly: Yeah, I see the spam now. Alright, banned. Try not to abuse the report button next time, yeah?")
    ],
    temperature=1.0,
    top_p=1.0,
    max_tokens=100,
    model=model
)
reply = response.choices[0].message.content
print(reply)
print("Latency: ", time.time()-quote_time)
json = (reply.split("```json"))[1]
json = json.replace("```", "").replace("false","False").replace("true", "True")
print(eval(json, {"__builtins__":{}}))

