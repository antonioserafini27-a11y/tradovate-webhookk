import sqlite3
from datetime import datetime


DB_FILE = "trades.db"


def init_db():
with sqlite3.connect(DB_FILE) as conn:
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS trades (
id INTEGER PRIMARY KEY AUTOINCREMENT,
action TEXT,
symbol TEXT,
price REAL,
quantity INTEGER,
timestamp TEXT
)
""")
conn.commit()


def save_trade(action, symbol, price, quantity):
with sqlite3.connect(DB_FILE) as conn:
c = conn.cursor()
c.execute("""
INSERT INTO trades (action, symbol, price, quantity, timestamp)
VALUES (?, ?, ?, ?, ?)
""", (action, symbol, price, quantity, datetime.utcnow().isoformat()))
conn.commit()


def get_trades():
with sqlite3.connect(DB_FILE) as conn:
c = conn.cursor()
c.execute("SELECT * FROM trades ORDER BY timestamp DESC")
rows = c.fetchall()
return rows
