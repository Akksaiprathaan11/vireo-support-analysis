"""
Streamlit dashboard for Vireo Audio Support Operations.
Run:
    streamlit run dashboard/app.py
"""
from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
sys.path.insert(0, str(ROOT / "src"))

st.set_page_config(
    page_title="Vireo Support Operations",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 Vireo Audio — Support Operations")
st.caption("Support ticket analysis | Jan 2025 – Jun 2026")

def load_csv(name):
    path = OUTPUT / name
    if not path.exists():
        st.error(f"{name} not found. Run: python src/analysis.py")
        st.stop()
    return pd.read_csv(path)

summary = load_csv("executive_summary.csv")
agents = load_csv("agent_scorecard.csv")
monthly = load_csv("monthly_metrics.csv")
violations = load_csv("policy_violations.csv")

def metric(name):
    row = summary.loc[summary["metric"] == name, "value"]
    return row.iloc[0] if not row.empty else None

tickets = int(metric("tickets_analyzed"))
csat = float(metric("overall_csat"))
breaches = int(metric("sla_breaches"))
sla_cost = int(metric("sla_credit_exposure_inr"))
contact_cost = int(metric("contact_cost_equivalent_inr"))
replacements = int(metric("replacement_tickets"))

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Tickets", f"{tickets:,}")
c2.metric("CSAT", f"{csat:.2f}/5")
c3.metric("SLA breaches", f"{breaches:,}")
c4.metric("SLA exposure", f"₹{sla_cost:,.0f}")
c5.metric("Contact cost eq.", f"₹{contact_cost/100000:.2f}L")
c6.metric("Replacements", f"{replacements:,}")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Executive Trends", "Agent Scorecard", "Policy / QA", "Recommendations"]
)

with tab1:
    st.subheader("Monthly performance")
    chart = monthly.set_index("month")[["tickets", "replacements", "refunds"]]
    st.line_chart(chart)

    st.subheader("CSAT trend")
    st.line_chart(monthly.set_index("month")[["csat"]])

    st.subheader("SLA breach rate")
    st.line_chart(monthly.set_index("month")[["sla_breach_rate"]])

    st.info(
        "Key signal: replacements increased from 144 in Dec 2025 "
        "to 290 in Feb 2026 (+101.4%), while Feb 2026 CSAT was 2.95/5."
    )

with tab2:
    st.subheader("Tier-1 agent scorecard")
    tier = agents[pd.to_numeric(agents["tier"], errors="coerce").eq(1)].copy()

    teams = ["All"] + sorted(tier["team"].dropna().unique().tolist())
    selected_team = st.selectbox("Team", teams)

    if selected_team != "All":
        tier = tier[tier["team"] == selected_team]

    display_cols = [
        "agent_id", "name", "team", "tickets",
        "csat_responses", "csat",
        "median_handle_minutes", "p90_handle_minutes",
        "sla_breach_rate", "transfers"
    ]

    st.dataframe(
        tier.sort_values("csat", ascending=True)[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Bottom 10 Tier-1 — flagged for review")
    st.dataframe(
        agents[
            pd.to_numeric(agents["tier"], errors="coerce").eq(1)
        ].sort_values("csat").head(10)[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Top 5 Tier-1 — bonus candidates")
    st.dataframe(
        agents[
            pd.to_numeric(agents["tier"], errors="coerce").eq(1)
        ].sort_values("csat", ascending=False).head(5)[display_cols],
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    st.subheader("Policy / QA findings")
    st.metric("Refund + replacement cases", len(violations))

    if len(violations):
        st.warning(
            "These tickets should be reviewed because the policy does not allow "
            "both refund and replacement for the same order."
        )
        st.dataframe(violations, use_container_width=True, hide_index=True)

    st.subheader("Financial planning equivalents")
    financial = pd.DataFrame({
        "Metric": [
            "Contact-cost equivalent",
            "Transfer-cost equivalent",
            "SLA credit exposure",
        ],
        "INR": [
            int(metric("contact_cost_equivalent_inr")),
            int(metric("transfer_cost_equivalent_inr")),
            int(metric("sla_credit_exposure_inr")),
        ],
    })
    st.dataframe(financial, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Recommended actions")

    st.markdown("""
### 1. Investigate the replacement workflow
Replacements rose **101.4%** from Dec 2025 to Feb 2026, reaching 290 in February,
while CSAT fell to **2.95/5**.

### 2. Improve first-response performance
There were **1,014 SLA breaches**, representing approximately **₹354,900**
of potential store-credit exposure.

### 3. Review agents, don't automatically retrain them
The bottom-ten list is a triage list. Tier-2 is excluded from the ranking,
and Logistics/Returns should be reviewed for process and queue effects before
attributing the outcome to individual agents.

### 4. Complete replacement economics when product costs are available
The exact replacement-cost calculation requires `products.csv`, which was not
provided with the supplied dataset.
""")

st.caption("Planning-equivalent costs are based on the supplied support policy, not accounting actuals.")
