import os
import time
from json import load
from openai import OpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from together import Together

with open("assets/info.json", "r") as f:
    DATA = load(f)
    EMOJI = DATA.get("emoji")

with open("res/server/help.json", "r") as f:
    HELP = load(f)
with open("res/server/profiles.json", "r") as f:
    Profiles = load(f)
with open("res/server/server_settings.json", "r") as f:
    Server_Settings = load(f)

with open("res/kellymemory/relations.json", "r") as f:
    Relation = load(f)
with open("res/kellymemory/chats.json", "r") as f:
    Chats = load(f)
with open("res/kellymemory/personality.json", "r") as f:
    Persona = load(f)
with open("res/kellymemory/logs.json", "r") as f:
    Logs = load(f)
with open("res/kellymemory/behaviors.json", "r") as f:
    Behaviours = load(f)

CLIENT1 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY"))#ai model connection
CLIENT2 = ChatCompletionsClient(endpoint="https://models.github.ai/inference",credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]))
CLIENT3 = Together()

client1_lastRequest = time.time()
client2_lastRequest = time.time()
client3_lastRequest = time.time()


def getResponse(usermessage, prompt, assistant="", client=3):
    messages= [SystemMessage(prompt)]
    messages2 = [{"role":"system","content": prompt}]
    
    if assistant != "":
        #adding history
        for msg in assistant.split("\n"):
            user = msg.split(":")
            if user[0] == "User":
                messages.append(UserMessage(user[1]))
                messages2.append({"role":"user","content":user[1]})
            else:
                messages.append(AssistantMessage(user[1]))
                messages2.append({"role":"assistant","content":user[1]})
    #adding current message
    messages.append(UserMessage(usermessage))
    messages2.append({"role":"user","content": usermessage})

    if client == 3:
        model="meta-llama/Llama-Vision-Free",
        try:
            if time.time() < client3_lastRequest + time.delay(seconds=15):
                time.sleep(client3_lastRequest + time.delay(seconds=15) - time.time())
            response = CLIENT3.chat.completions.create(
                model="meta-llama/Llama-Vision-Free",
                messages= messages2)
            client3_lastRequest = time.time()
        except:
            print("Model Changed")
            return getResponse(usermessage, prompt, assistant, client=1)
    elif client == 1:
        model= "deepseek/deepseek-prover-v2:free"
        if time.time() < client1_lastRequest + time.delay(seconds=15):
            time.sleep(client1_lastRequest + time.delay(seconds=15) - time.time())
        response = CLIENT1.chat.completions.create(
            messages= messages2,
            temperature=1.0,
            top_p=1.0,
            max_tokens=200,
            model= "deepseek/deepseek-prover-v2:free"
        )
        client1_lastRequest = time.time()
        if not response.choices:
            print("Model Changed")
            return getResponse(usermessage, prompt, assistant, client=2)
    elif client == 2:
        model= "deepseek/DeepSeek-V3-0324"
        if time.time() < client2_lastRequest + time.delay(seconds=15):
            time.sleep(client2_lastRequest + time.delay(seconds=15) - time.time())
        response = CLIENT2.complete(
                messages= messages,
                temperature=1.0,
                top_p=1.0,
                max_tokens=200,
                model= "deepseek/DeepSeek-V3-0324"
            )
        client2_lastRequest = time.time()
        
    print(f"#=====Response=====#\nModel: {model}\nPrompt: {prompt[0:5]}...{prompt[-5:]}\nINPUT: {usermessage}\nOUTPUT: {response.choices[0].message.content}")
    return response.choices[0].message.content

print("__init__ was runned")