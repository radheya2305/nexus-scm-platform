"""
NexusSCM - Executive Report & Board Memo Generator
Produces polished, executive-ready strategy memos and operations briefs.
"""

from typing import Dict, Any

def generate_nearshoring_executive_memo(
    scenario_data: Dict[str, Any],
    recommended_corridor: str = "Mexico (Nearshore USMCA)"
) -> str:
    """Generates an executive memo evaluating nearshoring landed costs and geopolitical tariffs."""
    results = scenario_data["corridor_results"]
    part_name = scenario_data["part_name"]
    volume = scenario_data["annual_volume"]
    china = results["China (Offshore Baseline)"]
    rec = results[recommended_corridor]

    spend_diff = rec["annual_spend_usd"] - china["annual_spend_usd"]
    capital_freed = china["total_capital_employed_usd"] - rec["total_capital_employed_usd"]
    carbon_diff = china["annual_carbon_metric_tons"] - rec["annual_carbon_metric_tons"]
    lead_time_days_saved = china["transit_time_days"] - rec["transit_time_days"]
    china_tariff_pct = int((china['tariff_cost'] / china['base_purchase_cost'] * 100.0)) if china['base_purchase_cost'] > 0 else 0

    memo = f"""# EXECUTIVE STRATEGY MEMORANDUM: GLOBAL SOURCING OPTIMIZATION
**TO:** Executive Leadership / VP of Global Supply Chain & Procurement  
**FROM:** Supply Chain Analytics & Strategy Team  
**DATE:** March 2025  
**SUBJECT:** Strategic Sourcing Evaluation & Total Landed Cost (TLC) Audit — {part_name}  

---

### 1. EXECUTIVE SUMMARY
A comprehensive Total Landed Cost (TLC) and geopolitical tariff risk audit was conducted for **{part_name}** (Annual Demand: **{volume:,} units**). 

While offshore procurement (China) presents lower initial factory-gate unit pricing, the compounding effects of:
1. Section 301 customs tariffs ({china_tariff_pct}%),
2. 38-day maritime transit pipeline inventory carrying financing, and
3. Safety stock buffer penalties driven by lead-time volatility ($\\sigma_L = 7.5\\text{{ days}}$)

...significantly erode margin advantages. 

**Core Recommendation:** Transition sourcing to **{recommended_corridor}**.

---

### 2. QUANTIFIED FINANCIAL & OPERATIONAL IMPACT

| Metric | China Baseline (Offshore) | {recommended_corridor} | Variance / Net Benefit |
| :--- | :--- | :--- | :--- |
| **Direct Landed Cost / Unit** | ${china['total_landed_cost']:.2f} | ${rec['total_landed_cost']:.2f} | **${rec['total_landed_cost'] - china['total_landed_cost']:+.2f} / unit** |
| **Annual Total Spend** | ${china['annual_spend_usd']:,.2f} | ${rec['annual_spend_usd']:,.2f} | **${spend_diff:+,.2f}** |
| **Working Capital Locked (Pipeline + Buffer)** | ${china['total_capital_employed_usd']:,.2f} | ${rec['total_capital_employed_usd']:,.2f} | **${capital_freed:,.2f} CASH RELEASED** |
| **Transit Lead Time** | {china['transit_time_days']:.0f} days | {rec['transit_time_days']:.0f} days | **{lead_time_days_saved:.0f} Days Compression** |
| **Carbon Footprint (Scope 3)** | {china['annual_carbon_metric_tons']:,.1f} MT CO2e | {rec['annual_carbon_metric_tons']:,.1f} MT CO2e | **{carbon_diff:,.1f} MT Reduction (-{carbon_diff/china['annual_carbon_metric_tons']*100:.1f}%)** |

---

### 3. STRATEGIC RISK MITIGATION
- **Tariff Elasticity:** Under a simulated +15% additional tariff shock, the China corridor total landed cost increases by ${china['base_purchase_cost']*0.15:.2f}/unit, whereas {recommended_corridor} qualifies under USMCA preferential zero-tariff treatment.
- **Service Level OTIF Resilience:** Compressing lead time to {rec['transit_time_days']:.0f} days reduces safety buffer requirements by {china['buffer_safety_units'] - rec['buffer_safety_units']:,.0f} units, eliminating stockout vulnerability during ocean port congestion.

### 4. RECOMMENDED NEXT STEPS
1. Initiate qualification audit with Monterrey Tier-1 manufacturing partner.
2. Establish dynamic cross-docking at Laredo to support JIT deliveries directly into Midwest DC.
3. Repurpose the **${capital_freed:,.2f}** in freed working capital into domestic automation and strategic S&OP visibility tooling.
"""
    return memo


def generate_10k_executive_audit_memo(
    company_data: Dict[str, Any],
    simulation_result: Dict[str, Any]
) -> str:
    """Generates a board-ready 10-K working capital value proposition memo."""
    c_name = company_data["name"]
    ticker = company_data["ticker"]
    ratios = company_data["calculated_ratios"]
    metrics = company_data["metrics"]

    memo = f"""# 10-K WORKING CAPITAL & SUPPLY CHAIN VALUE AUDIT
**TARGET ENTERPRISE:** {c_name} (NYSE: {ticker})  
**PREPARED BY:** Supply Chain Operations Strategy  
**SUBJECT:** Working Capital Liberation through Dynamic Multi-Echelon S&OP Optimization  

---

### 1. FINANCIAL DIAGNOSTIC OVERVIEW
Analysis of {c_name}'s recent SEC Form 10-K filings reveals substantial opportunities to optimize balance sheet velocity:

- **Annual Revenue:** ${metrics['revenue_usd_m']:,.1f}M | **COGS:** ${metrics['cogs_usd_m']:,.1f}M
- **Total Balance Sheet Inventory:** ${metrics['inventory_usd_m']:,.1f}M
- **Days Sales of Inventory (DSI):** **{ratios['dsi_days']:.1f} days**
- **Cash Conversion Cycle (CCC):** **{ratios['ccc_days']:.1f} days**
- **Daily Cost of Goods Sold:** **${metrics['cogs_usd_m']/365:.2f}M / day**

---

### 2. THE WORKING CAPITAL UNLOCK PROPOSITION
By introducing dynamic stochastic safety stock buffers and supplier lead-time variance pacing, {c_name} can target a conservative **{simulation_result['dsi_reduction_days']:.1f}-day compression in DSI** without impacting customer fill rates (OTIF).

**Quantified Value Creation:**
1. **Free Cash Flow (FCF) One-Time Release:**  
   $$\\Delta \\text{{Cash}} = {simulation_result['dsi_reduction_days']:.1f}\\text{{ days}} \\times \\${simulation_result['daily_cogs_usd_m']:.2f}\\text{{M/day}} = \\mathbf{{\\${simulation_result['free_cash_flow_unlocked_usd_m']:,.2f}\\text{{ Million}}}}$$
2. **Recurring Annual P&L Holding Cost Reduction:**  
   $$\\text{{Annual Savings}} = \\${simulation_result['free_cash_flow_unlocked_usd_m']:,.2f}\\text{{M}} \\times {simulation_result['wacc_percent']}\\% \\text{{ WACC}} = \\mathbf{{\\${simulation_result['annual_holding_cost_savings_usd_m']:,.2f}\\text{{ Million / year}}}}$$

---

### 3. IMPLEMENTATION WORKSTREAMS
1. **Lead Time Variance Contracting:** Penalize $\\sigma_L > 3$ days among Tier-1 suppliers to reduce DC buffer inflation.
2. **Multi-Echelon Risk Pooling:** Aggregate high-variance 'Z' category SKUs at Central Distribution Centers rather than regional depots.
3. **SKU Tail Rationalization:** Review the bottom 15% revenue-generating items driving disproportionate carrying cost.
"""
    return memo
