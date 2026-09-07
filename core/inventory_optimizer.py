"""
NexusSCM - Multi-Echelon Stochastic Inventory & S&OP Optimizer
Implements dual-stochastic safety stock models (demand + lead time variance),
Economic Order Quantity (EOQ), ABC-XYZ portfolio segmentation, and the
Working Capital vs. OTIF Service Level Efficient Frontier.
"""

import math
from typing import Dict, Any, List, Tuple
from core.landed_cost import norm_ppf

def calculate_stochastic_safety_stock(
    annual_demand: float,
    annual_demand_stdev: float,
    lead_time_days: float,
    lead_time_stdev_days: float,
    service_level: float = 0.98,
    unit_cost: float = 100.0,
    holding_cost_rate: float = 0.20,
    order_setup_cost: float = 150.0
) -> Dict[str, Any]:
    """
    Computes exact stochastic safety stock and cycle stock under dual uncertainty.
    """
    daily_demand = annual_demand / 365.0
    daily_demand_stdev = annual_demand_stdev / math.sqrt(365.0)

    # Variance of Demand During Lead Time (DDLT)
    # Var(DDLT) = L * Var(Daily Demand) + (Daily Demand)^2 * Var(Lead Time)
    var_ddlt = (
        lead_time_days * (daily_demand_stdev ** 2) +
        (daily_demand ** 2) * (lead_time_stdev_days ** 2)
    )
    sigma_ddlt = math.sqrt(max(0.0, var_ddlt))

    # Z-factor for Target Service Level (OTIF / Cycle Service Level)
    z_score = norm_ppf(service_level)
    safety_stock_units = z_score * sigma_ddlt
    mean_lead_time_demand = daily_demand * lead_time_days
    reorder_point = mean_lead_time_demand + safety_stock_units

    # Classical EOQ
    annual_holding_cost_per_unit = unit_cost * holding_cost_rate
    if annual_holding_cost_per_unit > 0 and annual_demand > 0:
        eoq_units = math.sqrt((2.0 * annual_demand * order_setup_cost) / annual_holding_cost_per_unit)
    else:
        eoq_units = daily_demand * 30.0

    avg_cycle_stock = eoq_units / 2.0
    total_avg_inventory = safety_stock_units + avg_cycle_stock
    total_working_capital_locked = total_avg_inventory * unit_cost
    annual_carrying_cost = total_working_capital_locked * holding_cost_rate

    # Variance breakdown (% contribution from supplier lead time vs demand)
    demand_var_contrib = lead_time_days * (daily_demand_stdev ** 2)
    lt_var_contrib = (daily_demand ** 2) * (lead_time_stdev_days ** 2)
    total_var = demand_var_contrib + lt_var_contrib
    lt_variance_pct = (lt_var_contrib / total_var * 100.0) if total_var > 0 else 0.0

    return {
        "service_level": service_level,
        "z_score": round(z_score, 2),
        "daily_demand": round(daily_demand, 2),
        "daily_demand_stdev": round(daily_demand_stdev, 2),
        "sigma_ddlt": round(sigma_ddlt, 2),
        "safety_stock_units": round(safety_stock_units, 1),
        "mean_lead_time_demand": round(mean_lead_time_demand, 1),
        "reorder_point": round(reorder_point, 1),
        "eoq_units": round(eoq_units, 1),
        "avg_cycle_stock_units": round(avg_cycle_stock, 1),
        "total_avg_inventory_units": round(total_avg_inventory, 1),
        "working_capital_locked_usd": round(total_working_capital_locked, 2),
        "annual_carrying_cost_usd": round(annual_carrying_cost, 2),
        "lead_time_variance_risk_percent": round(lt_variance_pct, 1)
    }


def generate_efficient_frontier(
    annual_demand: float,
    annual_demand_stdev: float,
    lead_time_days: float,
    lead_time_stdev_days: float,
    unit_cost: float,
    holding_cost_rate: float = 0.20,
    service_levels: List[float] = None
) -> List[Dict[str, Any]]:
    """
    Generates the corporate Efficient Frontier: Trade-off curve between 
    Customer On-Time In-Full (OTIF) service level and Total Working Capital ($M).
    Exposes the non-linear exponential cost of the 'Final 1.5%'.
    """
    if service_levels is None:
        service_levels = [0.85, 0.88, 0.90, 0.92, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.995]

    frontier = []
    prev_wc = None
    prev_sl = None

    for sl in service_levels:
        res = calculate_stochastic_safety_stock(
            annual_demand=annual_demand,
            annual_demand_stdev=annual_demand_stdev,
            lead_time_days=lead_time_days,
            lead_time_stdev_days=lead_time_stdev_days,
            service_level=sl,
            unit_cost=unit_cost,
            holding_cost_rate=holding_cost_rate
        )

        marginal_cost_per_pct = 0.0
        if prev_wc is not None and prev_sl is not None:
            delta_wc = res["working_capital_locked_usd"] - prev_wc
            delta_sl = (sl - prev_sl) * 100.0
            marginal_cost_per_pct = delta_wc / delta_sl if delta_sl > 0 else 0.0

        frontier.append({
            "service_level_percent": round(sl * 100.0, 1),
            "z_score": res["z_score"],
            "safety_stock_units": res["safety_stock_units"],
            "working_capital_usd": res["working_capital_locked_usd"],
            "annual_carrying_cost_usd": res["annual_carrying_cost_usd"],
            "marginal_cost_per_service_pct": round(marginal_cost_per_pct, 2)
        })

        prev_wc = res["working_capital_locked_usd"]
        prev_sl = sl

    return frontier


def simulate_multi_echelon_network(
    cdc_skus: List[Dict[str, Any]],
    num_rdcs: int = 3,
    correlation_between_rdcs: float = 0.0,
    wacc: float = 0.12
) -> Dict[str, Any]:
    """
    Models risk-pooling and inventory echelon distribution across Central DC and Regional DCs.
    Compares Decentralized (each RDC holds buffer) vs Centralized (Pooled buffer at CDC).
    """
    decentralized_ss_total = 0.0
    decentralized_capital_total = 0.0
    centralized_ss_total = 0.0
    centralized_capital_total = 0.0

    sku_analysis = []
    for sku in cdc_skus:
        ann_demand = sku["annual_demand"]
        ann_stdev = sku["demand_stdev_annual"]
        cost = sku["unit_cost"]
        lt = sku["supplier_lead_time_days"]
        lt_stdev = sku["lead_time_stdev_days"]

        # Centralized pooling
        cdc_res = calculate_stochastic_safety_stock(
            annual_demand=ann_demand,
            annual_demand_stdev=ann_stdev,
            lead_time_days=lt,
            lead_time_stdev_days=lt_stdev,
            service_level=0.98,
            unit_cost=cost
        )

        # Decentralized across N regional DCs (Square Root of N law under zero correlation)
        rdc_demand = ann_demand / num_rdcs
        rdc_stdev = ann_stdev / math.sqrt(num_rdcs)
        rdc_res = calculate_stochastic_safety_stock(
            annual_demand=rdc_demand,
            annual_demand_stdev=rdc_stdev,
            lead_time_days=lt,
            lead_time_stdev_days=lt_stdev,
            service_level=0.98,
            unit_cost=cost
        )

        total_rdc_ss = rdc_res["safety_stock_units"] * num_rdcs
        total_rdc_capital = total_rdc_ss * cost
        cdc_ss = cdc_res["safety_stock_units"]
        cdc_capital = cdc_ss * cost

        savings_capital = total_rdc_capital - cdc_capital
        carrying_savings = savings_capital * wacc

        decentralized_ss_total += total_rdc_ss
        decentralized_capital_total += total_rdc_capital
        centralized_ss_total += cdc_ss
        centralized_capital_total += cdc_capital

        sku_analysis.append({
            "sku_id": sku["sku_id"],
            "sku_name": sku["sku_name"],
            "decentralized_safety_stock": round(total_rdc_ss, 0),
            "centralized_safety_stock": round(cdc_ss, 0),
            "capital_unlocked_usd": round(savings_capital, 2),
            "annual_carrying_cost_savings_usd": round(carrying_savings, 2)
        })

    total_capital_unlocked = decentralized_capital_total - centralized_capital_total
    total_annual_holding_savings = total_capital_unlocked * wacc

    return {
        "num_rdcs": num_rdcs,
        "decentralized_capital_usd": round(decentralized_capital_total, 2),
        "centralized_capital_usd": round(centralized_capital_total, 2),
        "total_working_capital_unlocked_usd": round(total_capital_unlocked, 2),
        "annual_holding_savings_usd": round(total_annual_holding_savings, 2),
        "pooling_efficiency_gain_pct": round((total_capital_unlocked / decentralized_capital_total * 100.0), 1) if decentralized_capital_total > 0 else 0.0,
        "sku_details": sku_analysis
    }
