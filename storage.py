"""Local anonymous quiz and review records. No child identity is collected."""
import json, sqlite3
from pathlib import Path
from core import sha256, utc_now

def init_db(path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(path) as con:
        con.execute('CREATE TABLE IF NOT EXISTS quiz_runs (id INTEGER PRIMARY KEY, timestamp TEXT, lesson_id TEXT, correct INTEGER, total INTEGER, percent REAL, payload_hash TEXT)')
        con.execute('CREATE TABLE IF NOT EXISTS ai_reviews (id INTEGER PRIMARY KEY, timestamp TEXT, lesson_id TEXT, decision TEXT, reviewer TEXT, notes TEXT, response_hash TEXT, response_json TEXT)')

def save_quiz(path,lesson_id,result):
    init_db(path)
    with sqlite3.connect(path) as con:
        cur=con.execute('INSERT INTO quiz_runs (timestamp,lesson_id,correct,total,percent,payload_hash) VALUES (?,?,?,?,?,?)',
            (utc_now(),lesson_id,result['correct'],result['total'],result['percentage'],sha256(result)))
        return cur.lastrowid

def save_review(path,lesson_id,review,response):
    init_db(path)
    payload=response.model_dump() if hasattr(response,'model_dump') else response
    with sqlite3.connect(path) as con:
        cur=con.execute('INSERT INTO ai_reviews (timestamp,lesson_id,decision,reviewer,notes,response_hash,response_json) VALUES (?,?,?,?,?,?,?)',
            (utc_now(),lesson_id,review.decision,review.reviewer,review.notes,sha256(payload),json.dumps(payload,ensure_ascii=False)))
        return cur.lastrowid

def records(path,table):
    if table not in ('quiz_runs','ai_reviews'): raise ValueError('Unsupported table')
    init_db(path)
    with sqlite3.connect(path) as con:
        con.row_factory=sqlite3.Row
        return [dict(row) for row in con.execute(f'SELECT * FROM {table} ORDER BY id DESC')]
