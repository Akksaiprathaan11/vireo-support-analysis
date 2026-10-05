**Deployed Link: **https://vireo-support-analysis-lzcw7urfvtxjxihhjkwyza.streamlit.app/**
**
# Vireo Audio — Support Operations Analytics

A data-driven support operations analysis and decision dashboard built for Vireo Audio. The project analyzes customer support tickets to identify performance issues, SLA exposure, customer satisfaction trends, agent-level signals, refund/replacement patterns, and policy compliance opportunities.

---

## Overview

Vireo Audio's support team handles customer issues across chat, email, voice, and social channels.

The objective of this project is to turn raw support data into actionable answers for support leadership:

- How is customer satisfaction performing?
- Where are SLA breaches occurring?
- What is the operational cost exposure?
- Which Tier-1 agents should be reviewed or recognized?
- Are refunds and replacements following policy?
- What operational trends require investigation?
- Where can process improvements have the highest business impact?

The solution combines a reusable Python analytics pipeline with a Streamlit dashboard.

---

## Key Results

The analysis covers **11,750 support tickets** across the supplied dataset.

| Metric | Result |
|---|---:|
| Tickets analyzed | **11,750** |
| Completed tickets | **11,183** |
| CSAT responses | **4,947** |
| CSAT response rate | **44.24%** |
| Overall CSAT | **3.33 / 5** |
| Median handle time | **29 minutes** |
| P90 handle time | **4,496.8 minutes** |
| SLA breaches | **1,014** |
| SLA breach rate | **9.07%** |
| Potential SLA credit exposure | **₹3,54,900** |
| Contact-cost planning equivalent | **₹30.98 lakh** |
| Transfer-cost planning equivalent | **₹3,54,715** |
| Refund + replacement policy cases | **6** |

### Major operational signal

One of the strongest findings is the increase in replacement activity.

Replacement tickets increased from:

**144 in December 2025 → 290 in February 2026**

This represents approximately a **101.4% increase**.

At the same time, February 2026 CSAT fell to approximately **2.95 / 5**.

This suggests that the replacement workflow should be investigated as an operational priority rather than treating the problem only as an individual-agent performance issue.

---

## Business Questions Answered

### 1. Customer satisfaction

The pipeline calculates:

- Overall CSAT
- CSAT response rate
- CSAT by agent
- CSAT by team
- Monthly CSAT trends

Blank CSAT responses are excluded from CSAT averages.

---

### 2. SLA performance

SLA targets are calculated according to the supplied support policy:

| Channel | SLA Target |
|---|---:|
| Chat | 15 minutes |
| Voice | 2 hours |
| Social | 4 hours |
| Email | 8 hours |

A first-response time exceeding the channel target is classified as an SLA breach.

The policy assigns a **₹350 store-credit exposure per breach**.

The analysis identified:

**1,014 SLA breaches → ₹3,54,900 potential credit exposure**

---

### 3. Handle time

Handle time is calculated as:

```text
Resolution Time - First Response Time
```

Median and P90 are reported instead of relying only on the average because support resolution times have significant long-tail behavior.

---

## Important Timestamp Handling

The supplied support policy indicates that legacy resolution timestamps require UTC-to-IST reconstruction.

The pipeline therefore applies a **+5 hours 30 minutes correction** to legacy resolution timestamps before calculating handle time.

Without this correction, legacy records can produce invalid negative handle times.

This normalization is implemented in:

```text
src/data_cleaning.py
```

---

## Agent Performance

The project creates an agent scorecard containing:

- Agent ID
- Agent name
- Team
- Tier
- Ticket volume
- CSAT response count
- CSAT
- Median handle time
- Mean handle time
- P90 handle time
- SLA breach rate
- Transfer count

### Tier separation

Tier-2 agents are intentionally excluded from the Tier-1 bottom-ten ranking.

Tier-2 support is multi-touch and operationally different from Tier-1 frontline support. Comparing them directly using the same volume and handle-time metrics could produce misleading conclusions.

The bottom-ten list is therefore treated as:

> **Agents flagged for review**

rather than automatically labeling agents as poor performers or recommending retraining.

---

## Policy and QA Checks

The project checks refund and replacement activity against the supplied policy.

One important finding was:

**6 tickets contain both a positive refund amount and a replacement flag.**

These cases are surfaced as policy/QA review candidates.

The system does not automatically assume that an individual agent caused a policy violation.

---

## Cost Analysis

The project uses the support-policy planning costs:

| Channel / Activity | Planning Cost |
|---|---:|
| Chat | ₹210 |
| Email | ₹260 |
| Voice | ₹520 |
| Social | ₹240 |
| Internal transfer | ₹305 |
| SLA breach credit | ₹350 |

The completed tickets represent approximately:

**₹30.98 lakh in planning-equivalent contact cost**

and:

**₹3.55 lakh in transfer planning cost**

These figures are **planning equivalents**, not accounting or finance ledger values.

---

## Replacement Cost Limitation

Exact replacement cost was deliberately not estimated.

The policy requires replacement economics to use the product's unit cost plus the applicable shipping cost. The supplied assignment files did not include the required `products.csv` unit-cost data.

Rather than inventing a product cost or using an unsupported assumption, the project explicitly flags this as a limitation.

---

## AI Usage

AI was used as a development and analysis assistant for:

- Structuring the analysis approach
- Debugging code
- Reasoning about edge cases
- Interpreting operational patterns
- Improving the business narrative
- Reviewing methodology and presentation

The production analysis does **not** depend on paid LLM/API calls.

The actual KPI calculations are deterministic Python/Pandas operations, making the analysis reproducible and auditable.

No per-ticket paid LLM classification was introduced because it would add unnecessary cost and complexity for this dataset.

---

## Validation

The analysis includes checks for:

- Duplicate ticket IDs
- Duplicate agent IDs
- Duplicate order IDs
- Customer joins
- Agent joins
- Quoted order joins
- Missing values
- SLA calculations
- CSAT calculations
- Timestamp consistency
- Refund/replacement policy combinations

The supplied core datasets passed the implemented structural validation checks.

---

## Project Architecture

```text
Raw CSV Data
     │
     ▼
Data Cleaning
     │
     ├── Timestamp normalization
     ├── Join validation
     ├── SLA calculation
     └── Handle-time calculation
     │
     ▼
Analytics Pipeline
     │
     ├── CSAT analysis
     ├── Agent scorecard
     ├── Monthly trends
     ├── Cost analysis
     └── Policy checks
     │
     ▼
CSV Outputs
     │
     ├── Agent scorecard
     ├── Monthly metrics
     ├── Policy violations
     └── Executive summary
     │
     ▼
Streamlit Dashboard
```

---

## Repository Structure

```text
vireo-support-analysis/
│
├── data/
│   └── README.md
│
├── notebooks/
│   └── vireo_analysis.ipynb
│
├── src/
│   ├── data_cleaning.py
│   ├── analysis.py
│   └── policy_checks.py
│
├── output/
│   └── Generated analysis files
│
├── dashboard/
│   └── app.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

Raw assignment CSV files are intentionally excluded from the public repository.

---

## Generated Outputs

Running the analysis creates:

```text
output/
├── agent_scorecard.csv
├── monthly_metrics.csv
├── policy_violations.csv
├── executive_summary.csv
├── bottom10_tier1.csv
├── top5_tier1.csv
└── data_quality_summary.csv
```

### `agent_scorecard.csv`

Agent-level performance metrics.

### `monthly_metrics.csv`

Monthly ticket, CSAT, handle-time, SLA, refund, replacement, and cost metrics.

### `policy_violations.csv`

Tickets requiring refund/replacement policy review.

### `executive_summary.csv`

High-level business KPIs.

### `bottom10_tier1.csv`

Lowest observed CSAT among Tier-1 agents, intended as a review list.

### `top5_tier1.csv`

Highest observed CSAT among Tier-1 agents, intended as potential recognition/bonus candidates.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/vireo-support-analysis.git
cd vireo-support-analysis
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Analysis

Place the assignment CSV files in the local `data/` directory.

Then run:

```bash
python src/analysis.py
```

The generated results will be written to:

```text
output/
```

---

## Running the Dashboard

After running the analysis:

```bash
streamlit run dashboard/app.py
```

The dashboard provides:

### Executive Trends

- Ticket volume
- CSAT trends
- Replacement trends
- Refund trends
- SLA breach trends

### Agent Scorecard

- Tier-1 performance
- Bottom-ten review list
- Top-five recognition candidates

### Policy / QA

- Refund + replacement cases
- Financial planning equivalents
- Policy review information

### Recommendations

Business-focused actions based on the observed data.

---

## Limitations

This project intentionally documents its limitations rather than hiding them.

### Missing product cost data

`products.csv` was not supplied, so exact replacement cost is not calculated.

### No canonical issue ID

The dataset does not provide a unique identifier representing the underlying customer issue. Therefore, any repeat-contact analysis must use a proxy rather than claiming perfect issue-level accuracy.

### CSAT sample size

CSAT is only available for a subset of completed tickets. Agent rankings can therefore be sensitive to response volume.

### Tier/process effects

Logistics, Returns, and Tier-2 teams have operational characteristics that can naturally produce longer resolution times. Raw handle time should not be interpreted as individual agent productivity without context.

### Planning costs

Contact and transfer costs are based on the supplied policy and represent planning equivalents rather than accounting actuals.

---

## Key Recommendation

The strongest operational signal is not simply "retrain the lowest-performing agents."

The data suggests prioritizing:

1. **Investigating the replacement workflow**
2. **Reducing SLA breaches and associated credit exposure**
3. **Reviewing Tier-1 agents using CSAT together with SLA and ticket volume**
4. **Auditing refund/replacement policy exceptions**
5. **Obtaining product unit-cost data before calculating replacement economics**

The objective is to use the analysis to identify where operational changes can improve customer experience while reducing avoidable support cost.

---

## Reproducibility

The project is designed so that the same input data can be processed again using:

```bash
python src/analysis.py
```

The dashboard then reads the generated CSV outputs.

No paid LLM/API call is required to reproduce the analysis.

---

## Author

**Akksai Prathaan**

B.Tech Artificial Intelligence & Data Science

Focus areas: AI/ML, Generative AI, Data Analytics, Automation and Cybersecurity.
