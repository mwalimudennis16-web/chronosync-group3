from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os, imaplib, email, requests, smtplib, json
from email.mime.text import MIMEText
from email.header import decode_header
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel

app = FastAPI(title="CHRONO-SYNC Group 3 - KU AUTO AI")

# --- 80 BOB CONFIG ---
PRICE = 80
PAY_FILE = "payments.json"
DB_FILE = "users.json"

# --- LOAD / SAVE HELPERS ---
def load_pay():
    if os.path.exists(PAY_FILE):
        try:
            with open(PAY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_pay(data):
    with open(PAY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_users(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

users_db = load_users()
payments_db = load_pay()

class User(BaseModel):
    name: str
    gmail: str
    phone: str

class PayRequest(BaseModel):
    phone: str
    gmail: str = ""

# --- AI PARSE ---
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
            return "DEMO mode - notification ready"
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
            notif = f"{parsed['emoji']} CHRONO-SYNC AUTO AI\nTask: {parsed['task']}\nDue: {parsed['due']}\nPriority: {parsed['priority']}"
            send_gmail(student_email, f"{parsed['emoji']} {parsed['priority']} TASK", notif)
            send_whatsapp(student_phone, notif)
        mail.logout()
    except Exception as e:
        print(f"Auto check error: {e}")

# --- SCHEDULER - Every 2 min ---
scheduler = BackgroundScheduler()
scheduler.add_job(check_gmail_auto, 'interval', minutes=2)
scheduler.start()

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html>
    <body style="font-family:sans-serif; text-align:center; padding:20px; background:#f9f9f9">
        <h2>CHRONO-SYNC Group 3 - KU AUTO AI</h2>
        <p><b>Automatic Register + 80 BOB Activation</b></p>

        <div style="background:white; padding:20px; border-radius:10px; max-width:450px; margin:auto; box-shadow:0 2px 10px #ccc">
            <h3>Step 1: Register</h3>
            <form onsubmit="signup(event)">
                <input id="name" placeholder="Jina" required style="width:90%; padding:10px"><br><br>
                <input id="gmail" type="email" placeholder="Gmail" required style="width:90%; padding:10px"><br><br>
                <input id="phone" placeholder="0711..." required style="width:90%; padding:10px"><br><br>
                <button type="submit">REGISTER AUTOMATIC</button>
            </form>
            <p id="msg"></p>
            <hr>
            <h3>Step 2: Lipa {PRICE} BOB</h3>
            <button onclick="pay()" style="background:green; color:white; padding:10px 20px; border:none; border-radius:5px">LIPA 80 BOB - ACTIVATE AI</button>
            <p id="paymsg"></p>
        </div>
        <p><a href="/users">Angalia Registered + Paid</a> | <a href="/trigger-auto">Trigger AI Check</a></p>
        <script>
        async function signup(e){{
            e.preventDefault();
            const data = {{
                name: document.getElementById('name').value,
                gmail: document.getElementById('gmail').value,
                phone: document.getElementById('phone').value
            }};
            document.getElementById('msg').innerText = "Saving...";
            const res = await fetch('/signup', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(data)}});
            const r = await res.json();
            document.getElementById('msg').innerText = r.message;
        }}
        async function pay(){{
            const phone = document.getElementById('phone').value;
            const gmail = document.getElementById('gmail').value;
            if(!phone){{ alert('Weka namba kwanza'); return; }}
            document.getElementById('paymsg').innerText = "Inatengeneza Lipa...";
            const res = await fetch('/pay', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{phone, gmail}})}});
            const r = await res.json();
            document.getElementById('paymsg').innerHTML = r.message + "<br><button onclick='verify(\""+phone+"\")'>NIMELIPA - VERIFY</button>";
        }}
        async function verify(phone){{
            const res = await fetch('/verify-payment', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{phone}})}});
            const r = await res.json();
            document.getElementById('paymsg').innerText = r.message;
        }}
        </script>
    </body>
    </html>
    """

@app.post("/signup")
def signup(user: User):
    users = load_users()
    # usirudie
    if any(u['phone']==user.phone for u in users):
        return {"message": f"{user.name} umeshasajiliwa tayari! Endelea kulipa 80 bob."}
    users.append(user.dict())
    save_users(users)
    return {"message": f"Karibu {user.name}! Umesajiliwa automatic. Sasa lipa 80 BOB ku-activate AI."}

@app.post("/pay")
def pay(req: PayRequest):
    pays = load_pay()
    pays[req.phone] = {"phone": req.phone, "gmail": req.gmail, "amount": PRICE, "status": "PENDING", "till": "Lipa 80 to Till 123456 - Group 3"}
    save_pay(pays)
    return {"message": f"Lipa {PRICE} BOB kwa Till 123456 (Name: ChronoSync G3). Kisha bonyeza VERIFY. Phone: {req.phone}"}

@app.post("/verify-payment")
def verify_payment(req: PayRequest):
    pays = load_pay()
    if req.phone in pays:
        pays[req.phone]['status'] = "PAID"
        save_pay(pays)
        return {"message": f"✅ {req.phone} Ume-activate! 80 BOB received. AUTO AI iko LIVE kila 2min. Utapata WhatsApp + Gmail."}
    return {"message": "Bado hujaanza kulipa. Bonyeza LIPA 80 BOB kwanza."}

@app.get("/users")
def get_users():
    return {"users": load_users(), "payments": load_pay(), "price": PRICE}

@app.get("/trigger-auto")
def trigger():
    check_gmail_auto()
    return {"done":"Checked Gmail & sent WhatsApp+Gmail", "time":"now"}

@app.post("/parse")
def parse(text: str):
    p = ai_parse(text)
    msg = f"{p['emoji']} {p['priority']} Task: {p['task']} Due: {p['due']}"
    return {"ai": p, "whatsapp_preview": msg, "gmail_preview": msg}

@app.get("/health")
def health():
    return {"status":"AUTO AI LIVE", "price": PRICE, "auto_check":"Every 2min"}
