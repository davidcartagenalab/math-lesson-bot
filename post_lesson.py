from datetime import datetime
import json
import os
from notion_client import Client

# Replace these with your values
NOTION_TOKEN = "your_notion_token_here"
DATABASE_ID = "your_database_id_here"
LESSONS_DIR = "lessons"
COUNTER_FILE = "counter.json"
ALLOWED_DAYS = ["Monday", "Wednesday", "Friday"]

notion = Client(auth=NOTION_TOKEN)

today = datetime.today()
weekday = today.strftime("%A")

if weekday not in ALLOWED_DAYS:
    print("⏸️ Not a lesson day. Exiting.")
else:
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            counter = json.load(f)
    else:
        counter = {"last_posted": 0}

    next_index = counter["last_posted"] + 1
    lesson_path = os.path.join(LESSONS_DIR, f"lesson{next_index}.json")

    if not os.path.exists(lesson_path):
        print(f"⚠️ Lesson file not found: {lesson_path}")
    else:
        with open(lesson_path, "r") as f:
            lesson = json.load(f)

        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Topic": {"title": [{"text": {"content": lesson["title"]}}]},
                "Date": {"date": {"start": lesson["date"]}},
                "Status": {"status": {"name": lesson["status"]}}
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": lesson["content"]}}]
                    }
                }
            ]
        )

        counter["last_posted"] = next_index
        with open(COUNTER_FILE, "w") as f:
            json.dump(counter, f)

        print(f"✅ Posted lesson {next_index} to Notion.")