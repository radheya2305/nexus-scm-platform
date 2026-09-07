"""
NexusSCM - Corporate 10-K Working Capital & Cash Conversion Cycle (CCC) Engine
Calculates DSI, DSO, DPO, CCC, Net Working Capital, and simulates multi-million dollar
Free Cash Flow (FCF) releases from targeted inventory rationalization.
"""

import json
import os
from typing import Dict, Any, List

def load_corporate_profiles(data_path: str = None) -> Dict[str, Any]:
    """Loads audited corporate 10-K balance sheet profiles."""
    if data_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "corporate_10k_data.json")
    
    with open(data_path, "r") as f:
        return json.load(f)["companies"]


def compute_financial_ratios(
    revenue_m: float,
    cogs_m: float,
    inventory_m: float,
    ar_m: float,
    ap_m: float,
    wacc_pct: float = 8.5
) -> Dict[str, Any]:
    """
    Computes rigorous corporate working capital metrics.
    """
    dsi_days = (inventory_m / cogs_m * 365.0) if cogs_m > 0 else 0.0
    dso_days = (ar_m / revenue_m * 365.0) if revenue_m > 0 else 0.0
    dpo_days = (ap_m / cogs_m * 365.0) if cogs_m > 0 else 0.0
    ccc_days = dsi_days + dso_days - dpo_days

    net_working_capital_m = (inventory_m + ar_m) - ap_m
    nwc_to_revenue_pct = (net_working_capital_m / revenue_m * 100.0) if revenue_m > 0 else 0.0
    daily_cogs_m = cogs_m / 365.0

    return {
        "revenue_usd_m": revenue_m,
        "cogs_usd_m": cogs_m,
        "inventory_usd_m": inventory_m,
        "ar_usd_m": ar_m,
        "ap_usd_m": ap_m,
        "wacc_percent": wacc_pct,
        "daily_cogs_usd_m": round(daily_cogs_m, 2),
        "dsi_days": round(dsi_days, 2),
        "dso_days": round(dso_days, 2),
        "dpo_days": round(dpo_days, 2),
        "ccc_days": round(ccc_days, 2),
        "net_working_capital_usd_m": round(net_working_capital_m, 2),
        "nwc_to_revenue_percent": round(nwc_to_revenue_pct, 2)
    }


def simulate_working_capital_unlock(
    company_data: Dict[str, Any],
    target_dsi_reduction_days: float = 4.0
) -> Dict[str, Any]:
    """
    Simulates executive free cash flow release when SCM initiatives compress DSI.
    """
    metrics = company_data["metrics"]
    cogs_m = metrics["cogs_usd_m"]
    curr_inventory_m = metrics["inventory_usd_m"]
    wacc = metrics["wacc_percent"] / 100.0

    current_dsi = (curr_inventory_m / cogs_m * 365.0)
    target_dsi = max(5.0, current_dsi - target_dsi_reduction_days)

    daily_cogs_m = cogs_m / 365.0
    cash_unlocked_m = target_dsi_reduction_days * daily_cogs_m
    new_inventory_m = curr_inventory_m - cash_unlocked_m
    annual_carrying_cost_savings_m = cash_unlocked_m * wacc

    return {
        "company_name": company_data["name"],
        "ticker": company_data["ticker"],
        "current_dsi_days": round(current_dsi, 1),
        "target_dsi_days": round(target_dsi, 1),
        "dsi_reduction_days": round(target_dsi_reduction_days, 1),
        "daily_cogs_usd_m": round(daily_cogs_m, 2),
        "free_cash_flow_unlocked_usd_m": round(cash_unlocked_m, 2),
        "annual_holding_cost_savings_usd_m": round(annual_carrying_cost_savings_m, 2),
        "current_inventory_usd_m": curr_inventory_m,
        "optimized_inventory_usd_m": round(new_inventory_m, 2),
        "wacc_percent": metrics["wacc_percent"]
    }
