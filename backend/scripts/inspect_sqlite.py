import sqlite3
import json

con = sqlite3.connect("backend/technopie.db")
cur = con.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
results = {}

for t in tables:
    cnt = cur.execute(f'SELECT count(*) FROM "{t}";').fetchone()[0]
    sample = cur.execute(f'SELECT * FROM "{t}" LIMIT 1;').fetchone()
    cols = [d[0] for d in cur.description] if cur.description else []
    sample_dict = dict(zip(cols, sample)) if sample else None
    results[t] = {
        "row_count": cnt,
        "columns": cols,
        "sample": sample_dict
    }

con.close()
print(json.dumps(results, indent=2, default=str))
