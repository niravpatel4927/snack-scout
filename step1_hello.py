import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 1024,
    messages = [{"role": "user", "content": "Say hello in one sentence"}],

)

print(message.content[0].text)