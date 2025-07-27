# Personal Portfolio Coach – **Tech Bible v1**

*(light‑autonomy, human execution)*

---

## 0 Purpose

Deliver **actionable, portfolio‑aware buy/sell/hold guidance** every trading day by **08 : 45 IST**, framed around your
*long‑term wealth plan* (monthly income inflows, return target, maximum draw‑down, temperament).
Output (Slack + SMTP e‑mail Markdown) lets you adjust positions with **GTT or market orders** in Upstox.

*Key shift from the Options Radar*: we start with **your live holdings** (PostgreSQL mirror of Upstox) and look for
small, evidence‑backed nudges – accumulate quality when cheap, trim excess risk, deploy new cash promptly.

---

## 1 User Profile & Config

```yaml
# ~/.coach/config.yml
investor_id: "akshay"
salary_day: 25                # YYYY‑MM‑DD or day‑of‑month
monthly_inflow: 70_000        # INR
risk_profile: "moderate"      # conservative | moderate | aggressive
target_eq_weight: 0.75        # % of financial net‑worth
max_drawdown: 0.20            # portfolio peak‑to‑trough in INR
strategic_beta: 0.95          # vs NIFTY‑50
rebal_threshold: 5            # % drift that triggers action
capital_gains_budget: 0.03    # % of NAV you accept as taxable churn p.a.
liquidity_buffer_months: 6
slack_channel: "#portfolio‑coach"
email_to: "akshay@example.com"
```

*(can be edited in Vault UI; DAG pulls fresh on each run)*

---

## 2 Daily Schedule & Control Flow

| Time (IST)  | Micro‑service    | Action                                                                  |
| ----------- | ---------------- | ----------------------------------------------------------------------- |
| **07 : 30** | `pre_flight`     | Refresh tokens · pg\_healthcheck · price feed ping                      |
| **07 : 40** | `market_fetch`   | Pull EOD close, SGX‑Nifty, Nikkei 225, S\&P 500 futures, USD/INR, Brent |
| **07 : 50** | `portfolio_snap` | Query PostgreSQL → latest holdings, cost basis, realised P\&L           |
| **08 : 00** | `signal_run`     | Compute valuation z‑scores, drift vs targets, macro regime              |
| **08 : 15** | `idea_gen`       | GPT‑4o: draft trades (≤ 5)                                              |
| **08 : 25** | `risk_gate`      | Position‑sizing, VaR, liquidity, tax budget                             |
| **08 : 35** | `critic_vote`    | 3 × GPT‑3.5 red‑team *PASS ≥ 2*                                         |
| **08 : 45** | `report_push`    | Slack + e‑mail Markdown; attach copy‑paste GTT JSON                     |
| **18 : 30** | `post_mortem`    | Log realised fills, update performance DB                               |

*Monthly inflow allocation* runs automatically **T+1 of salary\_day**.

---

## 3 Data Inputs

| Feed / Table    | Source / Endpoint                                     | Purpose                      |
| --------------- | ----------------------------------------------------- | ---------------------------- |
| **Portfolio**   | `postgres://holdings.positions`                       | Units, cost, realised P\&L   |
| Cash ledger     | `postgres://holdings.cash_flows`                      | Salary, dividends, transfers |
| Live quotes     | Upstox WebSocket stream                               | Intraday P/L calc            |
| EOD OHLCV       | NSE BhavCopy S3 mirror                                | Valuation, momentum          |
| Fundamentals    | TTM EPS, book, P/E, ROE *(scraped or Refinitiv API)*  | Value screen                 |
| Global indices  | yFinance: SGX‑Nifty, S\&P 500, Nikkei 225, Brent, DXY | Macro overlay                |
| News sentiment  | RSS → GPT classifier                                  | Event risk                   |
| Vol metrics     | 20‑day HV, 30‑day IV (for F\&O names)                 | Hedge cost                   |
| Risk‑free curve | RBI SD yield curve API                                | Discounting                  |

All raw JSON parquet‑ised to `s3://portfolio‑coach/raw/{date}/`.

---

## 4 Decision Stack

1. **Allocation Drift**

   * Compare current weights vs `target_eq_weight`, sector caps, single‑name cap (5 % NAV).
   * *Trigger* when drift ≥ `rebal_threshold`.

2. **Valuation Screen**

   * Price‑to‑fair‑value z‑score `(P/E – peer_median) / peer_stdev`.
   * *Buy bias* for z ≤ –1, *Trim bias* for z ≥ +1.

3. **Momentum & Risk Overlay**

   * 50 d vs 200 d SMA, RSI(14), beta vs NIFTY.
   * Avoid catching falling knives unless macro regime is *risk‑on*.

4. **Cash Deployment**

   * `deployable = cash – liquidity_buffer` (6× monthly outflow).
   * Use **Kelly‑fraction** on expected Sharpe to size new buys.

5. **Tax & Liquidity Gate**

   * Keep projected STCG ≤ `capital_gains_budget` of NAV p.a.
   * Reject trades if 30‑day ADV < 20× intended value.

6. **LLM Idea Generator – `gpt‑4o`**

   * Prompt with holdings, metrics, gates → propose ≤ 5 orders.

7. **Critic Vote – `gpt‑3.5‑turbo‑128k`**

   * “Reject if thesis weak, violates gates, or over‑trades.”

8. **Back‑test Stub (EOD)**

   * 3‑year walk‑forward of similar *drift‑rebalance strategy*; require Sharpe ≥ 1.0.

9. **Confidence Score**
   `0.3·z_val + 0.3·critic_pass + 0.2·momentum_align + 0.2·backtest_hit%`
   *Green ≥ 0.75, Amber 0.6 – 0.74, Red < 0.6*

---

## 5 LLM Reasoning Pipeline

```mermaid
graph TD
A[Context<br/>Portfolio + Market] -->|T=0.25| B{gpt‑4o: DraftOrders}
B --> C[Critic 1‑3 (gpt‑3.5)]
C -->|PASS ≥ 2| D[RiskGate]
D --> E[ReportBuild]
```

Payload includes *each line item*: units, cost, WACC, valuation delta, drift%, ADV, tax impact.

---

## 6 Report / Delivery Format

````markdown
### 24 Jul 2025 – Portfolio Coach (08 : 45 IST)

| # | Action | Symbol | Qty | Limit | Confidence | Rationale |
|---|--------|--------|----:|------:|-----------:|-----------|
| 1 | **BUY** | TCS | 5 | ₹ 3 600 | 🟢 0.81 | Drift –4 %, P/E z = –1.2 |
| 2 | **TRIM** | HDFCBANK | –2 | ₹ 1 680 | 🟠 0.68 | Weight 7 % > cap, RSI 80 |
| 3 | **HOLD** | INFY | – | – | 🟢 0.77 | Fair value, momentum neutral |

*Copy‑paste‑ready GTT JSON block below.*  

```json
[
  {
    "transaction_type": "BUY",
    "instrument_token": "NSE_EQ|11536",
    "quantity": 5,
    "product": "I",
    "price": 3600
  },
  ...
]
````

*Risk banner* – prepend if projected draw‑down > `max_drawdown × 0.8`.

Monthly run **(26 th)** adds a *Cash‑Deployment Table* showing SIP allocations.

---

## 7 Risk & Governance

* Halt trading suggestions if **portfolio VaR(95) > 1.2 × max\_drawdown**.
* Any single suggestion’s notional ≤ NAV × 1 %.
* Tax guard: `STCG_to_date + projected_STCG_next` ≤ budget.
* All LLM prompts & outputs archived in S3 for audit.

---

## 8 Code Skeleton (Airflow + Pydantic)

```python
# dag.py
from airflow.decorators import dag, task
import pendulum, os, yaml
from data import feeds, portfolio
from engine import signals, llm, risk, report

UTC = pendulum.timezone("UTC")

@dag(schedule="30 7 * * 1-5", tz="Asia/Kolkata", catchup=False)
def portfolio_coach():

    @task()
    def pre_flight():
        feeds.health_check()
        portfolio.pg_health()

    @task()
    def market_fetch():
        return feeds.fetch_globals()

    @task()
    def portfolio_snap():
        return portfolio.fetch_positions()

    @task()
    def signal_run(pf, globals):
        return signals.compute(pf, globals)

    @task()
    def idea_gen(signal_ctx):
        return llm.draft(signal_ctx)

    @task()
    def risk_gate(ideas, signal_ctx):
        return risk.filter(ideas, signal_ctx)

    @task()
    def critic_vote(ideas):
        return llm.critique(ideas)

    @task()
    def report_push(final_ideas, signal_ctx):
        md = report.build(final_ideas, signal_ctx)
        report.push_slack(md)
        report.send_email(md)

    g = market_fetch()
    p = portfolio_snap()
    s = signal_run(p, g)
    i = idea_gen(s)
    r = risk_gate(i, s)
    c = critic_vote(r)
    pre_flight() >> report_push(c, s)

portfolio_coach()
```

---

## 9 Implementation Roadmap

1. **Foundations**

   * Create `holdings` schema in PostgreSQL (positions, cash\_flows).
   * Set up nightly ETL → S3 raw → Postgres history.

2. **Data Layer**

   * Extend `feeds.py` for global futures, RBI yield curve.
   * Build `fundamentals_service` (scrape or vendor API).

3. **Signal Engine**

   * Implement valuation, momentum, drift, risk metrics.
   * Unit‑test Pydantic models (`Position`, `TradeIdea`).

4. **LLM Layer**

   * Prompt templates for draft & critic; env‑switch model IDs.
   * Red‑team logic identical to Options Radar.

5. **Risk Engine**

   * VaR, STCG budget, liquidity check, max draw‑down tracking.

6. **Reporting**

   * Jinja Markdown template with colour bars & JSON fence.
   * Slack bot token & SMTP secrets to Vault.

7. **Monitoring**

   * Grafana dashboards: VaR, drift, realised vs target returns.
   * Alert rules on health‑check failures.

8. **Simulation & Back‑test**

   * Re‑run 3‑year history with drift‑rebalance logic; require Sharpe ≥ 1.0.

9. **Dry‑Run & Go‑Live**

   * Paper‑trade for 10 sessions, compare suggestions vs fills.
   * Sign‑off → PROD cut‑over.

---

## 10 Key Formulas

| Metric             | Formula                                          |
| ------------------ | ------------------------------------------------ |
| **Drift %**        | `(current_weight – target_weight)/target_weight` |
| **Fair‑Value Z**   | `(metric – peer_median) / peer_stdev`            |
| **Kelly‑fraction** | `edge / variance`                                |
| **VaR(95)**        | `portfolio_σ × 1.65 × sqrt(1 day)`               |

---
