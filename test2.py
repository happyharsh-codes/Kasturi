from openai import OpenAI
import time

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)
current_status = {"relation": 5, "mood": {"sad": 5}, "persona": {"mischevious": 15}}
cmd = {"ban": ["user", "reason"]}
prompt = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                Current status: {current_status}
                command: {None}
                Generate Json dict using kelly response and mood
                - command_performed: true/false/null(based on mood, tone and task difficulty)
                - command_params: (only when command is not None) (a dict with keys from list values having values from message)
                - respect: +/- (int)
                - mood_change: +/- (int)
                - personality_change: +/- (int)
                - info: [optional info about user to store important only]"""
msg = input("> ")
start = time.time()
completion = client.chat.completions.create(
  model="deepseek/deepseek-prover-v2:free",
  messages=[
    {
      "role": "system",
      "content": prompt
    },
    {
      "role": "user",
      "content": msg
    },
    {
        "role": "assistant",
        "content": "User: kelly can you ban @mkc for me he has been spamming non stop\nKelly: Aww sure thats a mods duty lemme get him banned"
    }
  ]
)
print(completion.choices[0].message.content)
print("Latency: ", (time.time()-start))