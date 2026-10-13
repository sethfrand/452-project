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
Ran 9 questions x 3 strategies (27 runs, see `results.json`). 23 of 27 produced SQL that executed; 4 failed with SQL errors.

| Strategy | Executed | Failed |
|---|---|---|
| zero_shot | 8/9 | Q3 |
| single_domain | 8/9 | Q3 |
| cross_domain | 7/9 | Q3, Q5 |

**Worked:** Q4 "Which runners are currently injured?" — all three strategies used `injury.end_date IS NULL` and returned Tom Kessler (shin splints). Q7 (routes run by every runner) and Q2 (average pace) were also consistent across strategies; single/cross-domain used a double `NOT EXISTS` for Q7, zero-shot used `HAVING COUNT(DISTINCT runner_id) = (SELECT COUNT(*) FROM runner)`, and both gave River Loop and Lakeshore Long Run.

**Didn't work:**
- Q3 (injuries per 100 km per shoe model) failed in every strategy with `no such column: r.distance_km` — distance lives on `route`, not `run`, and the query needed a multi-table aggregate.
- Q5 (never run on a trail): zero-shot returned an empty (wrong) result because `surface != 'trail'` plus `HAVING COUNT(...) = 0` is contradictory. Single-domain correctly used `NOT IN` and returned Tom Kessler and Walt Birch. Cross-domain errored (`no such column: r2.runner_id`).
- Q1 (most total km): every strategy used `ORDER BY ... LIMIT 1` and returned only Walt Birch, hiding the built-in tie with Tom Kessler (70 km each).
- Q6 (longest route in a retired pair of shoes): the correlated subqueries differ between strategies and aren't clearly correct; all return Tom Kessler and Walt Birch.
- Q8/Q9 ("most milage"): every strategy summed `duration_minutes` instead of `distance_km`, so "mileage" was really minutes (zero-shot even reported "312.0 miles"). Q8 was also answered inconsistently: runner name, a bare `runner_id` (3 = Ana Souza), or only a shoe id.

**Strategy differences:** Single-domain gave the best results (cleanest Q5, fewest failures alongside zero-shot). Cross-domain was not better than zero-shot here and was the only one to fail Q5. Cross-domain also returned the least informative columns (e.g. only a name or shoe id), which made answers like Q8 less useful. The tie in Q1 and the minutes-vs-km confusion in Q8/Q9 were not fixed by any strategy, suggesting the schema/prompt needs clearer hints rather than more context.
