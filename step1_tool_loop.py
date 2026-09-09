import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tools = [{"type": "web_search_20250305", "name": "web_search"}]

response = client.messages.create(
    model = 'claude-sonnet-5',
    max_tokens = 2048, 
    tools = tools, 
    messages = [{
        "role": "user",
        "content":("Find 3 snacks or desserts (chips, cookies, candy, pastries) "
            "that had a NEW limited-time release in the US in the last 7 days. "
            "For each, give the name, where you found it, and one sentence on it."
        )   
    }],
)

for block in response.content:
    print(f"--- block type: {block.type} ---")
    if block.type == "text":
        print(block.text)
    elif block.type == "server_tool_use":
        print(f"searched for {block.input}")






