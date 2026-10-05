"""
Main Vireo Audio Support Analytics pipeline.

Run from project root:
    python src/analysis.py
"""
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_cleaning import (
    load_data,
    validate_data,
    clean_tickets,
    merge_agent_data,
    SLA_CREDIT_INR,
)
from policy_checks import (
    refund_replacement_violations,
    refund_code_consistency,
    data_quality_checks,
)


def pct(series):
    return series.mean() * 100 if len(series) else 0.0


def build_agent_scorecard(completed):
    g = (
        completed.groupby(["agent_id", "name", "team", "tier"], dropna=False)
        .agg(
            tickets=("ticket_id", "count"),
            csat_responses=("csat_score", "count"),
            csat=("csat_score", "mean"),
            median_handle_minutes=("handle_minutes", "median"),
            mean_handle_minutes=("handle_minutes", "mean"),
            p90_handle_minutes=("handle_minutes", lambda x: x.quantile(0.90)),
            sla_breach_rate=("sla_breach", "mean"),
            transfers=("transfers", "sum"),
        )
        .reset_index()
    )
    g["sla_breach_rate"] *= 100
    g["csat"] = g["csat"].round(4)
    return g.sort_values(["tier", "csat"], ascending=[True, True])


def build_monthly_metrics(completed):
    monthly = (
        completed.groupby("month")
        .agg(
            tickets=("ticket_id", "count"),
            csat_responses=("csat_score", "count"),
            csat=("csat_score", "mean"),
            median_handle_minutes=("handle_minutes", "median"),
            p90_handle_minutes=("handle_minutes", lambda x: x.quantile(0.90)),
            sla_breaches=("sla_breach", "sum"),
            sla_breach_rate=("sla_breach", "mean"),
            replacements=("replacement_issued", lambda x: (x == "Y").sum()),
            refunds=("refund_amount_inr", lambda x: x.fillna(0).gt(0).sum()),
            refund_value_inr=("refund_amount_inr", "sum"),
            contact_cost_inr=("contact_cost_inr", "sum"),
            transfer_cost_inr=("transfer_cost_inr", "sum"),
        )
        .reset_index()
    )
    monthly["sla_breach_rate"] *= 100
    return monthly


def build_executive_summary(tickets, completed, violations, quality):
    breach_count = int(completed["sla_breach"].sum())
    csat_responses = int(completed["csat_score"].notna().sum())

    rows = [
        ("tickets_analyzed", len(tickets)),
        ("completed_tickets", len(completed)),
        ("csat_responses", csat_responses),
        ("csat_response_rate_pct", round(csat_responses / len(completed) * 100, 2)),
        ("overall_csat", round(completed["csat_score"].mean(), 4)),
        ("median_handle_minutes", round(completed["handle_minutes"].median(), 2)),
        ("p90_handle_minutes", round(completed["handle_minutes"].quantile(.90), 2)),
        ("sla_breaches", breach_count),
        ("sla_breach_rate_pct", round(breach_count / len(completed) * 100, 2)),
        ("sla_credit_exposure_inr", breach_count * SLA_CREDIT_INR),
        ("contact_cost_equivalent_inr", int(completed["contact_cost_inr"].sum())),
        ("transfer_cost_equivalent_inr", int(completed["transfer_cost_inr"].sum())),
        ("replacement_tickets", int((completed["replacement_issued"] == "Y").sum())),
        ("refund_tickets", int(completed["refund_amount_inr"].fillna(0).gt(0).sum())),
        ("refund_value_inr", int(completed["refund_amount_inr"].fillna(0).sum())),
        ("refund_replacement_policy_cases", len(violations)),
        ("data_quality_issues", sum(quality.values())),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    customers, agents, orders, tickets = load_data(data_dir)

    validation = validate_data(customers, agents, orders, tickets)
    validation.to_csv(output_dir / "data_quality_summary.csv")

    clean = clean_tickets(tickets)
    completed = clean[clean["completed"]].copy()
    agent_data = merge_agent_data(completed, agents)

    scorecard = build_agent_scorecard(agent_data)
    scorecard.to_csv(output_dir / "agent_scorecard.csv", index=False)

    monthly = build_monthly_metrics(completed)
    monthly.to_csv(output_dir / "monthly_metrics.csv", index=False)

    violations = refund_replacement_violations(clean)
    violations.to_csv(output_dir / "policy_violations.csv", index=False)

    quality = data_quality_checks(customers, agents, orders, tickets)
    summary = build_executive_summary(clean, completed, violations, quality)
    summary.to_csv(output_dir / "executive_summary.csv", index=False)

    # Extra review files requested by the business ask.
    tier1 = scorecard[pd.to_numeric(scorecard["tier"], errors="coerce").eq(1)].copy()
    tier1.sort_values("csat", ascending=True).head(10).to_csv(
        output_dir / "bottom10_tier1.csv", index=False
    )
    tier1.sort_values("csat", ascending=False).head(5).to_csv(
        output_dir / "top5_tier1.csv", index=False
    )

    print("\nVIREO SUPPORT ANALYSIS COMPLETE")
    print("=" * 55)
    print(summary.to_string(index=False))
    print("\nOutputs written to:", output_dir)


if __name__ == "__main__":
    main()
