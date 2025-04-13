# DIY ChatGPT-to-Notion Logger
# This script allows you to send a message (like "✅ Cardio bike 30 min") to this script manually,
# and it will log the data into a Notion database.
# You can run this locally and trigger it with a command-line message or future webhook.

import requests
import datetime
import os

# ----------- USER CONFIGURATION -----------
NOTION_TOKEN = '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'  # Get it from https://www.notion.so/my-integrations
DATABASE_ID = '1d34721e121980ef9c4ed1e605c1985b'           # Copy it from the Notion database URL

# ----------- MESSAGE INPUT (simulate ChatGPT message) -----------
# You can modify this to accept user input or webhook messages
chatgpt_message = "✅ Cardio bike 30 min"

# ----------- MESSAGE PARSING -----------
# Extract task name and duration from the message
# Example format: "✅ Cardio bike 30 min"
def parse_message(message):
    parts = message.strip("✅ ").split(" ")
    duration = parts[-2] + " " + parts[-1] if parts[-1].lower() in ["min", "minutes"] else ""
    task = " ".join(parts[:-2]) if duration else " ".join(parts)
    return task.strip(), duration.strip()

# ----------- NOTION API REQUEST -----------
# Sends a new row to the Notion database
def add_to_notion(task, duration):
    url = "https://api.notion.com/v1/pages"

    # Notion page payload
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Task": {"title": [{"text": {"content": task}}]},
            "Duration": {"number": duration},
            "Date": {"date": {"start": datetime.date.today().isoformat()}},
            "Source": {"rich_text": [{"text": {"content": "ChatGPT"}}]}
        }
    }

    # Headers with auth and versioning
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # Make the request
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("✅ Successfully added to Notion!")
    else:
        print(f"❌ Failed to add to Notion: {response.status_code}\n{response.text}")

# ----------- RUN -----------
if __name__ == "__main__":
    task, duration = parse_message(chatgpt_message)
    print(f"Parsed task: {task} | Duration: {duration}")
    add_to_notion(task, duration)
