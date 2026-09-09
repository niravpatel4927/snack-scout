import os, requests, json
from dotenv import load_dotenv
from storage import init_db, save_findings
from anthropic import Anthropic
from models import Finding
from datetime import date

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def gather_and_structure_findings():

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
    
    # Step 2: Gather findings
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
    
    # Step 2: Structure findings
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

    return findings


def notify_discord(findings):
    if not DISCORD_WEBHOOK_URL:
        print("No Discord webhook URL provided. Skipping notification.")
        return

    if not findings:
        return

    lines = [f"**{f.name}** ({f.category}) - {f.why_it_matches_you}\n{f.source_url}" for f in findings]
    requests.post(DISCORD_WEBHOOK_URL, json={"content": "\n\n".join(lines)})


def run():
    conn = init_db()
    try:
        findings = gather_and_structure_findings()
        before = set(row[0] for row in conn.execute("SELECT name FROM findings").fetchall())
        new_count = save_findings(conn, findings)
        new_ones = [f for f in findings if f.name not in before]
        print(f"Found {new_count} new findings this run.")
        notify_discord(new_ones)
    finally:
        conn.close()

if __name__ == "__main__":
    run()