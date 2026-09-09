import os, json
from dotenv import load_dotenv
from anthropic import Anthropic


load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def fake_taste_profile_lookup(category: str) -> str:
    # This is a fake function that simulates looking up a taste profile for a given category.
    # In a real implementation, this would query a database or an API to get the actual taste profile.
    # Pretend this hits your own database — for now it's hardcoded.
    
    profiles = {
        "snack": "loves salty/crunchy and also sweet, especially chip flavors and cookies and pastries",
        "restaurant": "loves trying new NYC openings, no seafood",
    }

    return profiles.get(category, "No taste profile available for this category.")


tools = [{
    "name": "get_taste_profile",
    "description": "Look up the user's taste profile for a category (snack or restaurant)",
    "input_schema": {
        "type": "object", 
        "properties": {
            "category": {
                "type": "string",
                "enum": ["snack", "restaurant"],
            },
        },
        "required": ["category"],
    },
}]

messages = [{"role": "user", "content": "What kind of new snack should I look for? Look to my taste profile first"}]

response = client.messages.create(model = "claude-sonnet-5", max_tokens = 1024, tools = tools, messages = messages)
print("First response stop reason: ", response.stop_reason) #should be "tool_use"

#Claude asked to call a tool - find that block, run it ourselves, send the result back
tool_use_block = next(b for b in response.content if b.type == "tool_use")
result = fake_taste_profile_lookup(**tool_use_block.input)

messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", 
                 "content": [{"type": "tool_result", "tool_use_id": tool_use_block.id, "content": result}]
    })

final = client.messages.create(model = "claude-sonnet-5", max_tokens = 1024, tools = tools, messages = messages)

for block in final.content:
    print(f"block type: {block.type}")
    if block.type == "text":
        print(block.text)
    else:
        print(block)   # see what actually came back