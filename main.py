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
