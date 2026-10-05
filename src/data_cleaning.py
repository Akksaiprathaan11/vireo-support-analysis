"""
Vireo Audio Support Analytics - data cleaning and feature engineering.
"""
from pathlib import Path
import pandas as pd

SLA_MINUTES = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}

CHANNEL_COSTS_INR = {
    "chat": 210,
    "email": 260,
    "voice": 520,
    "social": 240,
}

SLA_CREDIT_INR = 350
TRANSFER_COST_INR = 305


def _pick(base: Path, prefix: str) -> Path:
    matches = sorted(base.glob(f"{prefix}*.csv"))
    if not matches:
        raise FileNotFoundError(f"Could not find {prefix}*.csv in {base}")
    return matches[0]


def load_data(data_dir="data"):
    data_dir = Path(data_dir)
    customers = pd.read_csv(_pick(data_dir, "customers"))
    agents = pd.read_csv(_pick(data_dir, "agents"))
    orders = pd.read_csv(_pick(data_dir, "orders"))
    tickets = pd.read_csv(_pick(data_dir, "tickets"))
    return customers, agents, orders, tickets


def validate_data(customers, agents, orders, tickets):
    checks = {
        "customers_rows": len(customers),
        "customers_duplicate_rows": int(customers.duplicated().sum()),
        "agents_rows": len(agents),
        "agents_duplicate_ids": int(agents["agent_id"].duplicated().sum()),
        "orders_rows": len(orders),
        "orders_duplicate_ids": int(orders["order_id"].duplicated().sum()),
        "tickets_rows": len(tickets),
        "tickets_duplicate_ids": int(tickets["ticket_id"].duplicated().sum()),
        "tickets_missing_customer_join": int(
            (~tickets["customer_id"].isin(customers["customer_id"])).sum()
        ),
        "tickets_missing_agent_join": int(
            (~tickets["agent_id"].isin(agents["agent_id"])).sum()
        ),
        "tickets_missing_order_join": int(
            (
                tickets["order_id"].notna()
                & ~tickets["order_id"].isin(orders["order_id"])
            ).sum()
        ),
    }
    return pd.Series(checks, name="value")


def clean_tickets(tickets):
    df = tickets.copy()

    for col in ["created_at", "first_response_at", "resolved_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Policy: legacy resolution timestamps are UTC and need IST reconstruction.
    legacy = df["source_system"].eq("legacy_fd")
    df.loc[legacy, "resolved_at"] = (
        df.loc[legacy, "resolved_at"] + pd.Timedelta(hours=5, minutes=30)
    )

    df["sla_target_minutes"] = df["channel"].map(SLA_MINUTES)

    df["first_response_minutes"] = (
        df["first_response_at"] - df["created_at"]
    ).dt.total_seconds() / 60

    df["handle_minutes"] = (
        df["resolved_at"] - df["first_response_at"]
    ).dt.total_seconds() / 60

    df["completed"] = df["status"].isin(["resolved", "closed"])

    df["sla_breach"] = (
        df["first_response_minutes"] > df["sla_target_minutes"]
    ).fillna(False)

    df["contact_cost_inr"] = df["channel"].map(CHANNEL_COSTS_INR)
    df["transfer_cost_inr"] = df["transfers"].fillna(0) * TRANSFER_COST_INR
    df["sla_credit_exposure_inr"] = (
        df["sla_breach"].astype(int) * SLA_CREDIT_INR
    )

    df["csat_response"] = df["csat_score"].notna()
    df["month"] = df["created_at"].dt.to_period("M").astype(str)

    return df


def merge_agent_data(completed, agents):
    agent_cols = ["agent_id", "name", "site", "team", "shift", "tier"]
    return completed.merge(
        agents[agent_cols],
        on="agent_id",
        how="left",
        validate="many_to_one",
        suffixes=("", "_master"),
    )
