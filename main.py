from fastapi import FastAPI
import os, requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CHRONO-SYNC Group 3 - KU")

def parse_deadline(text: str):
    text_lower = text.lower()
    if any(w in text_lower for w in ["cat", "exam", "urgent", "final"]):
        priority = "URGENT"
        emoji = "🔴"
    elif "tomorrow" in text_lower or "today" in text_lower:
        priority = "TODAY"
        emoji = "🟡"
    else:
        priority = "LATER"
        emoji = "🟢"
    due = "Tomorrow 11am" if "tomorrow" in text_lower else "Soon"
    return {"task": text[:80], "due_date": due, "priority": priority, "emoji": emoji}

def send_whatsapp(to_number, message):
    token = os.getenv("WHATSAPP_TOKEN", "demo_token")
    phone_id = os.getenv("WHATSAPP_PHONE_ID", "demo_id")
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": message}}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=5)
        return r.json()
    except:
        return {"status": "Demo mode - add token in Render to send real WhatsApp"}

@app.get("/")
def home():
    return {"status": "CHRONO-SYNC Group 3 Running", "university": "Kenyatta University", "members": 5}

@app.post("/parse-email")
def parse_email(email_text: str, student_phone: str):
    parsed = parse_deadline(email_text)
    wa_msg = f"{parsed['emoji']} [{parsed['priority']}] - CHRONO-SYNC:\nTask: {parsed['task']}\nDue: {parsed['due_date']}\nReply ✅ DONE or ⏰ SNOOZE"
    result = send_whatsapp(student_phone, wa_msg)
    return {"parsed": parsed, "whatsapp": result, "message": "Synced!"}from fastapi import FastAPI
import os, requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CHRONO-SYNC Group 3 - KU")

def parse_deadline(text: str):
    text_lower = text.lower()
    if any(w in text_lower for w in ["cat", "exam", "urgent", "final"]):
        priority = "URGENT"
        emoji = "🔴"
    elif "tomorrow" in text_lower or "today" in text_lower:
        priority = "TODAY"
        emoji = "🟡"
    else:
        priority = "LATER"
        emoji = "🟢"
    due = "Tomorrow 11am" if "tomorrow" in text_lower else "Soon"
    return {"task": text[:80], "due_date": due, "priority": priority, "emoji": emoji}

def send_whatsapp(to_number, message):
    token = os.getenv("WHATSAPP_TOKEN", "demo_token")
    phone_id = os.getenv("WHATSAPP_PHONE_ID", "demo_id")
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": message}}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=5)
        return r.json()
    except:
        return {"status": "Demo mode - add token in Render to send real WhatsApp"}

@app.get("/")
def home():
    return {"status": "CHRONO-SYNC Group 3 Running", "university": "Kenyatta University", "members": 5}

@app.post("/parse-email")
def parse_email(email_text: str, student_phone: str):
    parsed = parse_deadline(email_text)
    wa_msg = f"{parsed['emoji']} [{parsed['priority']}] - CHRONO-SYNC:\nTask: {parsed['task']}\nDue: {parsed['due_date']}\nReply ✅ DONE or ⏰ SNOOZE"
    result = send_whatsapp(student_phone, wa_msg)
    return {"parsed": parsed, "whatsapp": result, "message": "Synced!"}
