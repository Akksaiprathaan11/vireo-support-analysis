# Vireo Audio — Support Operations Analysis

## Objective

Analyze Vireo Audio support tickets to identify:

- CSAT performance
- SLA performance and credit exposure
- Agent performance
- Monthly support trends
- Refund/replacement patterns
- Policy compliance
- Operational cost equivalents

## Dataset

The supplied dataset contains approximately:

- 11,750 support tickets
- 9,500 customers
- 15,500 orders
- 44 agents

## Key findings

- Overall completed-ticket CSAT: **3.33 / 5**
- CSAT response rate: **44.2%**
- SLA breaches: **1,014**
- Potential SLA store-credit exposure: **₹354,900**
- Contact-cost planning equivalent: **₹30.98 lakh**
- Transfer-cost planning equivalent: **₹354,715**
- Replacements increased from **144 in Dec 2025 to 290 in Feb 2026 (+101.4%)**
- Feb 2026 CSAT was **2.95 / 5**
- Six tickets have both a positive refund and replacement flag and should receive QA/policy review

## Important methodology

### Legacy timestamp correction

The supplied policy states that legacy resolution timestamps are stored in UTC while current helpdesk timestamps are displayed in IST. The pipeline therefore adds **5 hours 30 minutes** to `resolved_at` for `source_system == legacy_fd` before calculating handle time.

Without this correction, legacy tickets produce invalid negative handle times.

### Tiering

Tier-2 agents are not included in the Tier-1 bottom-ten ranking. Tier-2 work is multi-touch and should not be directly compared with Tier-1 on volume/handle metrics.

### Costing

Contact and transfer costs are policy planning equivalents:

- Chat: ₹210
- Email: ₹260
- Voice: ₹520
- Social: ₹240
- Transfer: ₹305
- SLA breach credit: ₹350

These are not accounting actuals.

### Replacement cost limitation

Exact replacement economics were not calculated because the supplied files did not include `products.csv` with unit-cost data. No assumed product cost was substituted.

## Run locally

```bash
pip install -r requirements.txt
python src/analysis.py
streamlit run dashboard/app.py
```

## Outputs

The pipeline creates:

- `output/agent_scorecard.csv`
- `output/monthly_metrics.csv`
- `output/policy_violations.csv`
- `output/executive_summary.csv`
- `output/bottom10_tier1.csv`
- `output/top5_tier1.csv`
- `output/data_quality_summary.csv`

## Project structure

```text
vireo-support-analysis/
├── data/
├── notebooks/
│   └── vireo_analysis.ipynb
├── src/
│   ├── data_cleaning.py
│   ├── analysis.py
│   └── policy_checks.py
├── output/
├── dashboard/
│   └── app.py
├── README.md
└── requirements.txt
```
