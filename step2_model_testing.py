import os, json
from anthropic import Anthropic
from dotenv import load_dotenv
from models import Finding
from datetime import date
from storage import init_db, save_findings

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

report_tool = {
    "name": "report_findings",
    "description": "Report the snack/dessert/restaurant findings in structured form.",
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "category": {"type": "string", "enum": ["snack, dessert", "restaurant"]},
                        "source_url": {"type": "string"},
                        "why_it_matches_you": {"type": "string"},
                    },
                    "required": ["name", "category", "source_url", "why_it_matches_you"],
                }, 
            }
        },
        "required": ["findings"],
    },
}


gather_response = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 2048,
    tools = [{"type": "web_search_20250305", "name": "web_search"}],
    messages = [{
        "role": "user",
        "content": "Search for 3 - 5 new limited-time snack/dessert releases in the US this week. List what you find with names, sources, and brief descriptions.",
    }]
)

gather_text = "".join(b.text for b in gather_response.content if b.type == "text")
print("---- Gathered text ---")
print(gather_text) # check is there really content here

structured_response = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 2048,
    tools = [report_tool],
    tool_choice = {"type": "tool", "name": "report_findings"}, #force exact tool
    messages = [{
        "role": "user", 
        "content": f"Convert the following findings into structured form using report_findings:\n\n{gather_text}",}
    ],
)


tool_call = next(b for b in structured_response.content if b.type == "tool_use" and b.name == "report_findings")
raw_findings = tool_call.input["findings"]
findings = [Finding(**f, date_found=date.today()) for f in raw_findings]

conn = init_db()
try:
    new_count = save_findings(conn, findings)
    print(f"Total findings this run: {len(findings)}")
    print(f"New rows inserted: {new_count}")
finally:
    conn.close()


