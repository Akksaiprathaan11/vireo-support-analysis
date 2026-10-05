"""
Policy and QA checks for Vireo Audio support tickets.
"""
import pandas as pd


def refund_replacement_violations(tickets):
    mask = (
        tickets["refund_amount_inr"].fillna(0).gt(0)
        & tickets["replacement_issued"].eq("Y")
    )
    cols = [
        "ticket_id",
        "agent_id",
        "refund_amount_inr",
        "refund_reason_code",
        "replacement_issued",
        "status",
        "category",
    ]
    return tickets.loc[mask, cols].sort_values("ticket_id")


def refund_code_consistency(tickets):
    refunds = tickets["refund_amount_inr"].fillna(0).gt(0)
    codes = tickets["refund_reason_code"].notna()

    return {
        "refunds_without_code": int((refunds & ~codes).sum()),
        "codes_without_refund": int((~refunds & codes).sum()),
        "refund_count": int(refunds.sum()),
    }


def data_quality_checks(customers, agents, orders, tickets):
    return {
        "customer_duplicate_rows": int(customers.duplicated().sum()),
        "agent_duplicate_ids": int(agents["agent_id"].duplicated().sum()),
        "order_duplicate_ids": int(orders["order_id"].duplicated().sum()),
        "ticket_duplicate_ids": int(tickets["ticket_id"].duplicated().sum()),
        "missing_ticket_customer": int(
            (~tickets["customer_id"].isin(customers["customer_id"])).sum()
        ),
        "missing_ticket_agent": int(
            (~tickets["agent_id"].isin(agents["agent_id"])).sum()
        ),
        "missing_quoted_order": int(
            (
                tickets["order_id"].notna()
                & ~tickets["order_id"].isin(orders["order_id"])
            ).sum()
        ),
    }
