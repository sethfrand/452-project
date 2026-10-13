import json, os, sqlite3, sys
from openai import OpenAI

here = os.path.dirname(os.path.abspath(__file__))
path = lambda f: os.path.join(here, f)

# Each person uses their own key: env var OPENAI_API_KEY, or marathon/config.json (git-ignored)
key = os.environ.get("OPENAI_API_KEY")
if not key and os.path.exists(path("config.json")):
    key = json.load(open(path("config.json")))["openaiKey"]
if not key:
    sys.exit('Set OPENAI_API_KEY or create marathon/config.json with {"openaiKey": "..."}')
client = OpenAI(api_key=key)
MODEL = "gpt-4o-mini"

# Fresh in-memory db each run
con = sqlite3.connect(":memory:")
schema = open(path("setup.sql")).read()
con.executescript(schema)
con.executescript(open(path("setupData.sql")).read())

def ask_gpt(prompt):
    r = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content

def clean_sql(text):
    if "```" in text:
        text = text.split("```", 2)[1]
        text = text.split("\n", 1)[1] if "\n" in text else text
    return text.strip().rstrip(";") + ";"

SQL_ONLY = "\nWrite one sqlite SELECT statement answering the question. Respond with SQL only."
# single-domain: example written against THIS schema
SINGLE = ("Q: Which runners have logged a run longer than 20 km?\n"
          "SQL: SELECT DISTINCT ru.name FROM run r JOIN runner ru ON r.runner_id=ru.runner_id "
          "JOIN route ro ON r.route_id=ro.route_id WHERE ro.distance_km>20;\n")
# cross-domain: example from an unrelated schema
CROSS = ("Example from a different database (library: book(book_id,title), loan(loan_id,book_id,member)):\n"
         "Q: Which books were loaned more than once?\n"
         "SQL: SELECT b.title FROM book b JOIN loan l ON b.book_id=l.book_id GROUP BY b.book_id HAVING COUNT(*)>1;\n\n")

strategies = {
    "zero_shot": lambda q: f"Schema:\n{schema}\n{SQL_ONLY}\nQ: {q}",
    "single_domain": lambda q: f"Schema:\n{schema}\n{SINGLE}{SQL_ONLY}\nQ: {q}",
    "cross_domain": lambda q: f"{CROSS}Schema:\n{schema}\n{SQL_ONLY}\nQ: {q}",
}

def answer(question, strategy):
    sql = clean_sql(ask_gpt(strategies[strategy](question)))
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    friendly = ask_gpt(
        f"Question: {question}\nSQL used: {sql}\nColumns: {cols}\nRows: {rows}\n"
        "Answer the question concisely in plain English using the actual names/values in the rows.")
    return sql, rows, friendly

if __name__ == "__main__":
    qs = [l.split(". ", 1)[1].replace("(my own) ", "").strip()
          for l in open(path("questions.md")) if l[:1].isdigit()]
    out = []
    for s in strategies:
        for q in qs:
            try:
                sql, rows, friendly = answer(q, s); err = None
            except Exception as e:
                sql = rows = friendly = None; err = str(e)
            print(f"[{s}] {q}\n  {sql}\n  {rows}\n  {friendly or err}\n")
            out.append(dict(strategy=s, question=q, sql=sql, rows=rows, friendly=friendly, error=err))
    json.dump(out, open(path("results.json"), "w"), indent=2, default=str)
