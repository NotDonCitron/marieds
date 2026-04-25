import sqlite3
import os
from datetime import datetime
from scrapers.base import ListingResult

DB_PATH = "seen_listings.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_listings (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                platform TEXT NOT NULL,
                price REAL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            )
        """)
        conn.commit()

def has_seen(result: ListingResult) -> bool:
    if not os.path.exists(DB_PATH):
        init_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id FROM seen_listings WHERE id = ?",
            (result.id,)
        ).fetchone()
    return row is not None

def save_seen(result: ListingResult):
    now = datetime.utcnow().isoformat()
    if not os.path.exists(DB_PATH):
        init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO seen_listings
            (id, url, title, platform, price, first_seen_at, last_seen_at)
            VALUES (
                ?, ?, ?, ?, ?,
                COALESCE((SELECT first_seen_at FROM seen_listings WHERE id = ?), ?),
                ?, ?
            )
        """, (
            result.id, result.url, result.title, result.platform, result.price,
            result.id, now, now, now
        ))
        conn.commit()
