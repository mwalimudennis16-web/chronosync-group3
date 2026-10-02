from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json, os
from datetime import datetime

app = FastAPI()

# --- SETTINGS ZAKO ---
MY_MPESA_NUMBER = "0798471867"  # PESA INAINGIA HAPA DIRECT!
MY_NAME = "Dennis"
FREE_DAYS = 8
PRICE = 80

DB_FILE = "users.json"
users_db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f:
            users_db = json.load(f)
    except:
        users_db = []

class User(BaseModel):
    name: str
    gmail: str
    phone: str

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><body style="font-family:sans-serif; text-align:center; padding:20px">
        <h2>ChronoSync Group 3</h2>
        <h3 style="color:green">{FREE_DAYS} DAYS FREE, then {PRICE} Bob!</h3>
        <form onsubmit="signup(event)">
            <input id="name" placeholder="Jina" required><br><br>
            <input id="gmail" type="email" placeholder="Gmail" required><br><br>
            <input id="phone" placeholder="07..." required><br><br>
            <button style="padding:12px 20px; background:black; color:white; border-radius:8px; font-size:16px">ANZA
