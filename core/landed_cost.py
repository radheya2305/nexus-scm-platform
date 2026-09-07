"""
NexusSCM - Total Landed Cost (TLC) & Nearshoring Decision Engine
Models geopolitical sourcing trade-offs: purchasing, freight, tariffs, 
pipeline inventory financing, lead-time volatility buffers, and ESG emissions.
"""

import math
from typing import Dict, Any, List

try:
    from scipy.stats import norm
    def norm_ppf(p: float) -> float:
        if p <= 0.0 or p >= 1.0:
            raise ValueError("Probability p must be strictly between 0 and 1.")
        return float(norm.ppf(p))
except ImportError:
    # Pure Python fallback using Beasley-Springer-Moro algorithm
    def norm_ppf(p: float) -> float:
        if p <= 0.0 or p >= 1.0:
            raise ValueError("Probability p must be strictly between 0 and 1.")
        a = [2.50662823884, -18.61500062529, 41.39119773534, -25.44106049637]
        b = [-8.47351093090, 23.08336743743, -21.06224101826, 3.13082909833]
        c = [0.3374754822726147, 0.9761690190917186, 0.1607979714918209,
             0.0276438810333863, 0.0038405729373609, 0.0003951896511919,
             0.0000321767881768, 0.0000002888167364, 0.0000003960315187]
        y = p - 0.5
        if abs(y) < 0.42:
            r = y * y
            x = y * (((a[3]*r + a[2])*r + a[1])*r + a[0]) / ((((b[3]*r + b[2])*r + b[1])*r + b[0])*r + 1.0)
        else:
            r = p if y < 0 else 1.0 - p
            r = math.log(-math.log(r))
            x = c[0] + r*(c[1] + r*(c[2] + r*(c[3] + r*(c[4] + r*(c[5] + r*(c[6] + r*(c[7] + r*c[8])))))))
            if y < 0:
                x = -x
        return x


def calculate_corridor_tlc(
    base_purchase_cost: float,
    freight_cost: float,
    handling_drayage: float,
    tariff_rate: float,
    transit_time_days: float,
    lead_time_stdev_days: float,
    wacc: float,
    annual_volume: int,
    service_level: float = 0.98,
    carbon_kg_per_unit: float = 1.0,
    moq: int = 500
) -> Dict[str, Any]:
    """
    Computes rigorous Total Landed Cost (TLC) incorporating hidden financing and volatility costs.
    """
    z_score = norm_ppf(service_level)
    daily_demand = annual_volume / 365.0

    # 1. Direct landed invoice components
    tariff_cost = base_purchase_cost * tariff_rate
    duty_paid_purchase = base_purchase_cost + tariff_cost
    logistics_cost = freight_cost + handling_drayage

    # 2. Pipeline Working Capital (In-transit inventory holding cost)
    transit_working_capital_cost = (
        base_purchase_cost * wacc * (transit_time_days / 365.0)
    )

    # 3. Lead Time Volatility Buffer Penalty
    buffer_safety_units = z_score * daily_demand * lead_time_stdev_days
    annual_buffer_holding_cost = buffer_safety_units * base_purchase_cost * wacc
    buffer_cost_per_unit = annual_buffer_holding_cost / annual_volume if annual_volume > 0 else 0.0

    # 4. Total Landed Cost per unit
    total_landed_cost = (
        duty_paid_purchase +
        logistics_cost +
        transit_working_capital_cost +
        buffer_cost_per_unit
    )

    # 5. Aggregate Enterprise Metrics
    annual_spend = total_landed_cost * annual_volume
    pipeline_capital_locked = daily_demand * transit_time_days * base_purchase_cost
    buffer_capital_locked = buffer_safety_units * base_purchase_cost
    total_capital_employed = pipeline_capital_locked + buffer_capital_locked
    annual_carbon_mt = (annual_volume * carbon_kg_per_unit) / 1000.0

    return {
        "base_purchase_cost": round(base_purchase_cost, 2),
        "tariff_cost": round(tariff_cost, 2),
        "duty_paid_purchase": round(duty_paid_purchase, 2),
        "freight_cost": round(freight_cost, 2),
        "handling_drayage": round(handling_drayage, 2),
        "logistics_cost": round(logistics_cost, 2),
        "transit_working_capital_cost": round(transit_working_capital_cost, 2),
        "buffer_cost_per_unit": round(buffer_cost_per_unit, 2),
        "total_landed_cost": round(total_landed_cost, 2),
        "annual_spend_usd": round(annual_spend, 2),
        "pipeline_capital_locked_usd": round(pipeline_capital_locked, 2),
        "buffer_capital_locked_usd": round(buffer_capital_locked, 2),
        "total_capital_employed_usd": round(total_capital_employed, 2),
        "buffer_safety_units": round(buffer_safety_units, 0),
        "transit_time_days": transit_time_days,
        "lead_time_stdev_days": lead_time_stdev_days,
        "annual_carbon_metric_tons": round(annual_carbon_mt, 1),
        "z_score": round(z_score, 2)
    }


def compare_sourcing_corridors(
    part_name: str,
    annual_volume: int,
    wacc: float = 0.12,
    service_level: float = 0.98,
    china_tariff: float = 0.25,
    mexico_tariff: float = 0.00,
    vietnam_tariff: float = 0.10,
    domestic_tariff: float = 0.00,
    china_base_cost: float = 100.0,
    mexico_cost_premium: float = 0.10,
    vietnam_cost_premium: float = 0.02,
    domestic_cost_premium: float = 0.35,
) -> Dict[str, Any]:
    """
    Executes an enterprise comparative sourcing trade-off analysis across 4 primary corridors.
    """
    corridors = {
        "China (Offshore Baseline)": {
            "origin": "Shanghai",
            "mode": "Ocean + Rail Intermodal",
            "base_cost": china_base_cost,
            "freight": 14.50,
            "drayage": 4.20,
            "tariff": china_tariff,
            "transit_days": 38.0,
            "stdev_days": 7.5,
            "carbon_kg": 18.4
        },
        "Mexico (Nearshore USMCA)": {
            "origin": "Monterrey",
            "mode": "Cross-Border Drayage + TL",
            "base_cost": china_base_cost * (1.0 + mexico_cost_premium),
            "freight": 5.80,
            "drayage": 1.50,
            "tariff": mexico_tariff,
            "transit_days": 6.0,
            "stdev_days": 1.2,
            "carbon_kg": 4.8
        },
        "Vietnam (Alt Offshore)": {
            "origin": "Hai Phong",
            "mode": "Ocean + Rail Intermodal",
            "base_cost": china_base_cost * (1.0 + vietnam_cost_premium),
            "freight": 16.20,
            "drayage": 4.50,
            "tariff": vietnam_tariff,
            "transit_days": 42.0,
            "stdev_days": 8.0,
            "carbon_kg": 20.1
        },
        "US Domestic (Reshore)": {
            "origin": "Midwest / Ohio Valley",
            "mode": "Regional Dedicated Truckload",
            "base_cost": china_base_cost * (1.0 + domestic_cost_premium),
            "freight": 3.20,
            "drayage": 0.00,
            "tariff": domestic_tariff,
            "transit_days": 2.0,
            "stdev_days": 0.4,
            "carbon_kg": 2.2
        }
    }

    results = {}
    for name, params in corridors.items():
        tlc = calculate_corridor_tlc(
            base_purchase_cost=params["base_cost"],
            freight_cost=params["freight"],
            handling_drayage=params["drayage"],
            tariff_rate=params["tariff"],
            transit_time_days=params["transit_days"],
            lead_time_stdev_days=params["stdev_days"],
            wacc=wacc,
            annual_volume=annual_volume,
            service_level=service_level,
            carbon_kg_per_unit=params["carbon_kg"]
        )
        tlc["origin"] = params["origin"]
        tlc["mode"] = params["mode"]
        results[name] = tlc

    baseline_spend = results["China (Offshore Baseline)"]["annual_spend_usd"]
    baseline_capital = results["China (Offshore Baseline)"]["total_capital_employed_usd"]

    for name in results:
        results[name]["annual_spend_variance_vs_china"] = round(
            results[name]["annual_spend_usd"] - baseline_spend, 2
        )
        results[name]["capital_released_vs_china"] = round(
            baseline_capital - results[name]["total_capital_employed_usd"], 2
        )

    return {
        "part_name": part_name,
        "annual_volume": annual_volume,
        "wacc": wacc,
        "service_level": service_level,
        "corridor_results": results
    }


def tariff_sensitivity_curve(
    base_purchase_cost: float,
    freight_cost: float,
    transit_days: float,
    stdev_days: float,
    wacc: float,
    annual_volume: int,
    tariffs: List[float] = [0.0, 0.10, 0.25, 0.35, 0.50, 0.60]
) -> List[Dict[str, Any]]:
    """
    Computes landed cost sensitivity across varied tariff stress scenarios.
    """
    curve = []
    for t in tariffs:
        res = calculate_corridor_tlc(
            base_purchase_cost=base_purchase_cost,
            freight_cost=freight_cost,
            handling_drayage=3.5,
            tariff_rate=t,
            transit_time_days=transit_days,
            lead_time_stdev_days=stdev_days,
            wacc=wacc,
            annual_volume=annual_volume
        )
        curve.append({
            "tariff_percent": round(t * 100, 1),
            "total_landed_cost": res["total_landed_cost"],
            "annual_spend_usd": res["annual_spend_usd"]
        })
    return curve
