from fastapi import FastAPI, Request
from datetime import datetime
import httpx
import sqlite3
import os

from admin.panel import router as admin_router

TPAY_TOKEN = os.getenv("TPAY_TOKEN")
TPAY_API = "https://api.tpay.com/transactions"

# poprawne położenie bazy:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite")

app = FastAPI()
app.include_router(admin_router)

def db_exec(q, params=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(q, params)
    conn.commit()
    conn.close()

# tworzymy BAZĘ i TABELĘ tutaj:
db_exec("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    transaction_id TEXT,
    status TEXT,
    amount REAL,
    created_at TEXT
)
""")

@app.post("/create_transaction")
async def create_transaction(payload: dict):
    headers = {"Authorization": f"Bearer {TPAY_TOKEN}", "Content-Type": "application/json"}

    body = {
        "amount": payload["amount"],
        "description": f"BLIK Test {payload['user_id']}",
        "payer": {
            "email": "test@example.com",
            "name": f"user_{payload['user_id']}"
        },
        "pay": {"groupId": 150}
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(TPAY_API, headers=headers, json=body)
        data = r.json()

    db_exec(
        "INSERT INTO payments (user_id, transaction_id, status, amount, created_at) VALUES (?, ?, 'pending', ?, ?)",
        (payload["user_id"], data["transactionId"], payload["amount"], datetime.utcnow().isoformat())
    )

    return {"transaction_id": data["transactionId"]}

@app.post("/send_blik_code")
async def send_blik_code(payload: dict):
    url = f"{TPAY_API}/{payload['transaction_id']}/pay"

    headers = {"Authorization": f"Bearer {TPAY_TOKEN}", "Content-Type": "application/json"}
    body = {
        "groupId": 150,
        "blikPaymentData": {"blikToken": int(payload["blik_code"])}
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=body)
        return r.json()

@app.post("/webhook/tpay")
async def webhook_tpay(request: Request):
    body = await request.json()
    status = body.get("payments", {}).get("status")
    transaction_id = body.get("transactionId")

    if status == "success":
        db_exec("UPDATE payments SET status='success' WHERE transaction_id=?", (transaction_id,))
    elif status == "failed":
        db_exec("UPDATE payments SET status='failed' WHERE transaction_id=?", (transaction_id,))

    return {"ok": True}
