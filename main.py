from fastapi import FastAPI
import os, imaplib, email, requests, smtplib
from email.mime.text import MIMEText
from email.header import decode_header
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI(title="CHRONO-SYNC Group 3 - KU AUTO AI")

def ai_parse(text: str):
    t = text.lower()
    if any(w in t for w in ["cat","exam","urgent","deadline","final","assignment"]):
        return {"task": text[:100], "due": "TOMORROW 9AM", "priority": "URGENT", "emoji": "🔴"}
    if "tomorrow" in t or "today" in t:
        return {"task": text[:100], "due": "Tomorrow 11am", "priority": "TODAY", "emoji": "🟡"}
    return {"task": text[:100], "due": "This Week", "priority": "LATER", "emoji": "🟢"}

def send_gmail(to_email, subject, body):
    try:
        sender = os.getenv("GMAIL_USER")
        pwd = os.getenv("GMAIL_PASS")
        if not sender or not pwd:
            return "Add GMAIL_USER & GMAIL_PASS in Render ENV"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(sender, pwd)
            s.send_message(msg)
        return f"Gmail sent to {to_email}"
    except Exception as e:
        return f"Gmail fail: {e}"

def send_whatsapp(to_number, message):
    try:
        token = os.getenv("WHATSAPP_TOKEN")
        phone_id = os.getenv("WHATSAPP_PHONE_ID")
        if not token:
            return "DEMO mode - notification ready, add WhatsApp token to send real"
        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"messaging_product":"whatsapp","to":to_number,"type":"text","text":{"body":message}}
        r = requests.post(url, headers=headers, json=data, timeout=10)
        return f"WhatsApp sent {r.status_code}"
    except Exception as e:
        return f"WhatsApp fail: {e}"

def check_gmail_auto():
    try:
        user = os.getenv("GMAIL_USER")
        pwd = os.getenv("GMAIL_PASS")
        student_phone = os.getenv("STUDENT_PHONE","254700000000")
        student_email = os.getenv("STUDENT_EMAIL", user)
        if not user or not pwd: return
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pwd)
        mail.select("INBOX")
        _, data = mail.search(None, '(UNSEEN)')
        for e_id in data[0].split()[-5:]:
            _, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subj = str(decode_header(msg["Subject"])[0][0])
            body = ""
            if msg.is_multipart():
                for p in msg.walk():
                    if p.get_content_type()=="text/plain":
                        body = p.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")
            parsed = ai_parse(f"{subj} {body}")
            notif = f"{parsed['emoji']} CHRONO-SYNC AUTO AI\nTask: {parsed['task']}\nDue: {parsed['due']}\nPriority: {parsed['priority']}\n\nReply DONE/SNOOZE"
            send_gmail(student_email, f"{parsed['emoji']} {parsed['priority']} TASK", notif)
            send_whatsapp(student_phone, notif)
        mail.logout()
    except Exception as e:
        print(e)

scheduler = BackgroundScheduler()
scheduler.add_job(check_gmail_auto, 'interval', minutes=2)
scheduler.start()

@app.get("/")
def home():
    return {"status":"AUTO AI LIVE","KU":"Group 3","auto_check":"Every 2min","notify":["Gmail","WhatsApp"]}

@app.get("/trigger-auto")
def trigger():
    check_gmail_auto()
    return {"done":"Checked Gmail & sent WhatsApp+Gmail"}

@app.post("/parse")
def parse(text: str):
    p = ai_parse(text)
    msg = f"{p['emoji']} {p['priority']} Task: {p['task']} Due: {p['due']}"
    return {"ai": p, "whatsapp_preview": msg, "gmail_preview": msg}
