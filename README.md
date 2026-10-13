# Marathon Training Log — AI + SQL

**Purpose:** records runners, their shoes, routes, individual runs and injuries, so you can ask things like which shoe models are tied to the most injuries per kilometer.

Run (use your *own* OpenAI key; never commit it):
```
pip install openai
export OPENAI_API_KEY=sk-...
python3 marathon/bot.py
```
Files: `setup.sql`, `setupData.sql`, `bot.py` (zero-shot, single-domain, cross-domain), `questions.md` (7 questions), `schema.md` (diagram), `results.json` (written after a run).

Note: Q1 has a built-in tie (Tom and Walt both 70 km) to see whether GPT/answer handles ties.

## Results
_Not run yet — requires a personal OpenAI API key. After running, fill in a question that worked, one that didn't, and any differences between strategies._
