"""
NexusSCM - Enterprise Supply Chain Decision Intelligence Platform
Designed & Engineered by WashU Olin Supply Chain Management
Live Executive Workbench: Nearshoring TLC, Multi-Echelon S&OP, and 10-K Working Capital Audit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import json

from core.landed_cost import (
    calculate_corridor_tlc,
    compare_sourcing_corridors,
    tariff_sensitivity_curve
)
from core.inventory_optimizer import (
    calculate_stochastic_safety_stock,
    generate_efficient_frontier,
    simulate_multi_echelon_network
)
from core.financial_benchmarks import (
    load_corporate_profiles,
    compute_financial_ratios,
    simulate_working_capital_unlock
)
from core.report_generator import (
    generate_nearshoring_executive_memo,
    generate_10k_executive_audit_memo
)

# Page configuration
st.set_page_config(
    page_title="NexusSCM | Enterprise Supply Chain Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for executive appearance (optimized for dark & light modes)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
    }
    .sub-header {
        font-size: 1.05rem;
        color: #CBD5E1 !important;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
    }
    .metric-val {
        font-size: 1.7rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }
    .badge-washu {
        background-color: #BA0C2F;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Load Sample Data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
corporate_data = load_corporate_profiles(os.path.join(BASE_DIR, "data", "corporate_10k_data.json"))
sku_df = pd.read_csv(os.path.join(BASE_DIR, "data", "sample_skus.csv"))

# Sidebar Header
with st.sidebar:
    st.markdown('<span class="badge-washu">WashU Olin SCM</span>', unsafe_allow_html=True)
    st.title("NexusSCM Platform")
    st.caption("Enterprise Supply Chain & S&OP Intelligence Workbench")
    st.markdown("---")
    
    app_mode = st.radio(
        "Select Decision Intelligence Module:",
        [
            "1. Nearshoring & Total Landed Cost (TLC)",
            "2. Multi-Echelon S&OP & Safety Stock",
            "3. Corporate 10-K Working Capital Audit",
            "4. Executive Outreach & Career Toolkit"
        ]
    )
    
    st.markdown("---")
    st.info(
        "💡 **Executive Value Prop:** Built to bridge mathematical operations engineering with "
        "C-suite working capital optimization (Free Cash Flow, OTIF, Landed Margins)."
    )

# -------------------------------------------------------------------------------------------------
# MODULE 1: NEARSHORING & TOTAL LANDED COST (TLC) ENGINE
# -------------------------------------------------------------------------------------------------
if app_mode == "1. Nearshoring & Total Landed Cost (TLC)":
    st.markdown('<div class="main-header">Global Nearshoring & Total Landed Cost (TLC) Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Evaluating offshore maritime corridors vs. USMCA nearshoring under dynamic tariff and lead-time shocks.</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        part_name = st.text_input("Component / Assembly Name", value="Industrial Solenoid Valve")
    with col2:
        annual_volume = st.number_input("Annual Demand (Units)", value=25000, step=5000)
    with col3:
        china_base_cost = st.number_input("China Ex-Works Unit Cost ($)", value=95.00, step=5.0)
    with col4:
        wacc = st.slider("Cost of Capital (WACC %)", min_value=6.0, max_value=18.0, value=11.5, step=0.5) / 100.0

    st.markdown("##### ⚙️ Geopolitical Scenario Controls")
    c_s1, c_s2, c_s3, c_s4 = st.columns(4)
    with c_s1:
        china_tariff = st.slider("China Section 301 Tariff (%)", 0, 60, 25, 5) / 100.0
    with c_s2:
        mexico_premium = st.slider("Mexico Factory Premium (%)", 0, 30, 10, 2) / 100.0
    with c_s3:
        target_otif = st.slider("Target OTIF Service Level (%)", 90.0, 99.5, 98.0, 0.5) / 100.0
    with c_s4:
        mexico_tariff = st.slider("Mexico USMCA Tariff (%)", 0, 20, 0, 5) / 100.0

    # Run Analysis
    analysis = compare_sourcing_corridors(
        part_name=part_name,
        annual_volume=annual_volume,
        wacc=wacc,
        service_level=target_otif,
        china_tariff=china_tariff,
        mexico_tariff=mexico_tariff,
        china_base_cost=china_base_cost,
        mexico_cost_premium=mexico_premium
    )
    res = analysis["corridor_results"]
    china = res["China (Offshore Baseline)"]
    mexico = res["Mexico (Nearshore USMCA)"]
    domestic = res["US Domestic (Reshore)"]
    vietnam = res["Vietnam (Alt Offshore)"]

    # Top KPI summary cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Recommended Corridor</div>
            <div class="metric-val" style="font-size:1.2rem; color:#059669;">Mexico (Nearshore)</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Unit TLC Difference</div>
            <div class="metric-val" style="color:#059669;">${mexico['total_landed_cost'] - china['total_landed_cost']:+.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Working Capital Released</div>
            <div class="metric-val" style="color:#0284C7;">${mexico['capital_released_vs_china']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Transit Time Compressed</div>
            <div class="metric-val" style="color:#7C3AED;">-{china['transit_time_days'] - mexico['transit_time_days']:.0f} Days</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Visualizations: Stacked Cost Breakdown & Sensitivity
    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        st.subheader("📊 Total Landed Cost (TLC) Component Breakdown")
        categories = list(res.keys())
        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(name='Ex-Works Base', x=categories, y=[res[c]['base_purchase_cost'] for c in categories], marker_color='#1E293B'))
        fig_bars.add_trace(go.Bar(name='Customs & Tariffs', x=categories, y=[res[c]['tariff_cost'] for c in categories], marker_color='#EF4444'))
        fig_bars.add_trace(go.Bar(name='Freight & Drayage', x=categories, y=[res[c]['logistics_cost'] for c in categories], marker_color='#F59E0B'))
        fig_bars.add_trace(go.Bar(name='Pipeline Financing (WACC)', x=categories, y=[res[c]['transit_working_capital_cost'] for c in categories], marker_color='#3B82F6'))
        fig_bars.add_trace(go.Bar(name='Volatility Buffer Penalty', x=categories, y=[res[c]['buffer_cost_per_unit'] for c in categories], marker_color='#8B5CF6'))

        fig_bars.update_layout(
            barmode='stack',
            yaxis_title="USD ($) per Unit",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bars, use_container_width=True)

    with chart_col2:
        st.subheader("📈 Tariff Elasticity Curve")
        tariffs = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60]
        curve = tariff_sensitivity_curve(
            base_purchase_cost=china_base_cost,
            freight_cost=14.50,
            transit_days=38.0,
            stdev_days=7.5,
            wacc=wacc,
            annual_volume=annual_volume,
            tariffs=tariffs
        )
        t_df = pd.DataFrame(curve)
        fig_curve = px.line(
            t_df, x="tariff_percent", y="total_landed_cost",
            title="China TLC vs. Tariff Hike %",
            labels={"tariff_percent": "Section 301 Tariff (%)", "total_landed_cost": "Total Landed Cost ($/unit)"},
            markers=True
        )
        # Add horizontal line for Mexico TLC
        fig_curve.add_hline(
            y=mexico["total_landed_cost"], line_dash="dash", line_color="green",
            annotation_text="Mexico TLC Breakeven"
        )
        fig_curve.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_curve, use_container_width=True)

    # Detailed Comparison Table
    st.subheader("📋 Corridor Decision Matrix")
    matrix_rows = []
    for c_name, d in res.items():
        matrix_rows.append({
            "Corridor": c_name,
            "Transit (Days)": f"{d['transit_time_days']:.0f} ± {d['lead_time_stdev_days']:.1f}",
            "Landed Cost ($)": f"${d['total_landed_cost']:.2f}",
            "Annual Spend ($M)": f"${d['annual_spend_usd']/1e6:.2f}M",
            "Working Capital ($)": f"${d['total_capital_employed_usd']:,.0f}",
            "Spend Delta vs. China": f"${d['annual_spend_variance_vs_china']:+,.0f}",
            "Carbon (MT CO2e)": f"{d['annual_carbon_metric_tons']:,.1f}"
        })
    st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)

    # Executive Memo Export
    with st.expander("📄 Generate Board-Ready Sourcing Decision Memo"):
        memo_text = generate_nearshoring_executive_memo(analysis)
        st.markdown(memo_text)
        st.download_button(
            label="📥 Download Executive Memo (.md)",
            data=memo_text,
            file_name=f"Executive_Sourcing_Memo_{part_name.replace(' ', '_')}.md",
            mime="text/markdown"
        )

# -------------------------------------------------------------------------------------------------
# MODULE 2: MULTI-ECHELON S&OP & SAFETY STOCK OPTIMIZER
# -------------------------------------------------------------------------------------------------
elif app_mode == "2. Multi-Echelon S&OP & Safety Stock":
    st.markdown('<div class="main-header">Multi-Echelon Stochastic Inventory & S&OP Optimizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Optimizing the Efficient Frontier: OTIF Service Level (%) vs. Total Working Capital Invested ($M).</div>', unsafe_allow_html=True)

    st.subheader("1. SKU Parameter Selection")
    sku_options = sku_df["sku_name"].tolist()
    selected_sku_name = st.selectbox("Select SKU from Enterprise Master Catalog:", sku_options)
    curr_row = sku_df[sku_df["sku_name"] == selected_sku_name].iloc[0]

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        ann_demand = st.number_input("Annual Demand (Units)", value=int(curr_row["annual_demand"]), step=1000)
    with p2:
        ann_demand_stdev = st.number_input("Annual Demand StDev (σ_D)", value=int(curr_row["demand_stdev_annual"]), step=500)
    with p3:
        unit_cost = st.number_input("Unit Cost ($)", value=float(curr_row["unit_cost"]), step=10.0)
    with p4:
        holding_rate = st.slider("Annual Carrying Cost Rate (%)", 10.0, 30.0, float(curr_row["holding_cost_rate"]*100), 1.0) / 100.0

    p5, p6, p7, p8 = st.columns(4)
    with p5:
        supplier_lt = st.slider("Supplier Lead Time (Days)", 5, 90, int(curr_row["supplier_lead_time_days"]), 1)
    with p6:
        supplier_lt_stdev = st.slider("Lead Time StDev (σ_L Days)", 0.0, 20.0, float(curr_row["lead_time_stdev_days"]), 0.5)
    with p7:
        target_sl = st.slider("Target Service Level (OTIF %)", 85.0, 99.5, 98.0, 0.5) / 100.0
    with p8:
        category_tag = st.text_input("ABC-XYZ Category", value=curr_row["category"], disabled=True)

    # Compute Stochastic Inventory
    inv_res = calculate_stochastic_safety_stock(
        annual_demand=ann_demand,
        annual_demand_stdev=ann_demand_stdev,
        lead_time_days=supplier_lt,
        lead_time_stdev_days=supplier_lt_stdev,
        service_level=target_sl,
        unit_cost=unit_cost,
        holding_cost_rate=holding_rate
    )

    # Summary KPIs
    sk1, sk2, sk3, sk4 = st.columns(4)
    with sk1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Calculated Safety Stock</div>
            <div class="metric-val">{inv_res['safety_stock_units']:,.0f} Units</div>
        </div>
        """, unsafe_allow_html=True)
    with sk2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Reorder Point (ROP)</div>
            <div class="metric-val">{inv_res['reorder_point']:,.0f} Units</div>
        </div>
        """, unsafe_allow_html=True)
    with sk3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Working Capital Tied Up</div>
            <div class="metric-val" style="color:#0284C7;">${inv_res['working_capital_locked_usd']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with sk4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Supplier Variance Risk Share</div>
            <div class="metric-val" style="color:#DC2626;">{inv_res['lead_time_variance_risk_percent']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Efficient Frontier Visualization
    f_col1, f_col2 = st.columns([3, 2])
    with f_col1:
        st.subheader("📈 The Efficient Frontier: OTIF vs. Working Capital")
        st.caption("Demonstrating the exponential 'Cost of the Final 1.5%'.")
        
        frontier_data = generate_efficient_frontier(
            annual_demand=ann_demand,
            annual_demand_stdev=ann_demand_stdev,
            lead_time_days=supplier_lt,
            lead_time_stdev_days=supplier_lt_stdev,
            unit_cost=unit_cost,
            holding_cost_rate=holding_rate
        )
        f_df = pd.DataFrame(frontier_data)
        
        fig_frontier = go.Figure()
        fig_frontier.add_trace(go.Scatter(
            x=f_df["service_level_percent"],
            y=f_df["working_capital_usd"],
            mode='lines+markers',
            name='Efficient Frontier',
            line=dict(color='#0284C7', width=3),
            marker=dict(size=8, color='#0F172A')
        ))
        # Add marker for current target service level
        fig_frontier.add_trace(go.Scatter(
            x=[target_sl * 100.0],
            y=[inv_res["working_capital_locked_usd"]],
            mode='markers',
            name='Current Target',
            marker=dict(size=14, color='#DC2626', symbol='star')
        ))

        fig_frontier.update_layout(
            xaxis_title="Target OTIF Service Level (%)",
            yaxis_title="Total Working Capital Required ($)",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_frontier, use_container_width=True)

    with f_col2:
        st.subheader("🏢 Multi-Echelon Risk Pooling Analysis")
        st.caption("Centralization Savings (Square Root Law) across 3 Regional DCs.")
        
        skus_list = sku_df.to_dict(orient="records")
        pooling_res = simulate_multi_echelon_network(skus_list, num_rdcs=3)
        
        fig_pool = go.Figure(data=[
            go.Bar(name='Decentralized (3 RDCs)', x=['Working Capital'], y=[pooling_res['decentralized_capital_usd']], marker_color='#64748B'),
            go.Bar(name='Centralized (CDC)', x=['Working Capital'], y=[pooling_res['centralized_capital_usd']], marker_color='#10B981')
        ])
        fig_pool.update_layout(
            barmode='group',
            yaxis_title="Working Capital ($)",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_pool, use_container_width=True)
        st.success(
            f"💡 **Centralization Benefit:** Risk pooling across the 3 RDCs unlocks **${pooling_res['total_working_capital_unlocked_usd']:,.0f}** "
            f"in working capital and saves **${pooling_res['annual_holding_savings_usd']:,.0f}** annually in holding costs."
        )

# -------------------------------------------------------------------------------------------------
# MODULE 3: CORPORATE 10-K WORKING CAPITAL AUDIT (OPTION 3)
# -------------------------------------------------------------------------------------------------
elif app_mode == "3. Corporate 10-K Working Capital Audit":
    st.markdown('<div class="main-header">Corporate 10-K Working Capital Value Audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Reverse-engineering audited balance sheets to identify multi-million dollar Free Cash Flow (FCF) releases.</div>', unsafe_allow_html=True)

    # Select Target Company
    company_tickers = list(corporate_data.keys())
    company_labels = [f"{corporate_data[t]['name']} ({t}) - {corporate_data[t]['headquarters']}" for t in company_tickers]
    
    selected_idx = st.selectbox("Select Target Enterprise to Audit:", range(len(company_labels)), format_func=lambda x: company_labels[x])
    target_ticker = company_tickers[selected_idx]
    c_data = corporate_data[target_ticker]

    st.markdown(f"#### 🏢 Enterprise Profile: **{c_data['name']}**")
    st.info(f"📌 **Operational Context:** {c_data['executive_context']}")

    # Display 10-K Financial Diagnostics
    met = c_data["metrics"]
    rat = c_data["calculated_ratios"]

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Annual Revenue", f"${met['revenue_usd_m']:,.0f}M")
    with m2:
        st.metric("Total Inventory", f"${met['inventory_usd_m']:,.0f}M")
    with m3:
        st.metric("Days Sales Inv (DSI)", f"{rat['dsi_days']:.1f} Days")
    with m4:
        st.metric("Cash Conv Cycle (CCC)", f"{rat['ccc_days']:.1f} Days")
    with m5:
        st.metric("Daily COGS Burn", f"${met['cogs_usd_m']/365:.1f}M / day")

    st.markdown("---")

    # Interactive Cash Unlock Simulator
    st.subheader("💡 The Working Capital Unlock Simulator")
    st.caption("Simulate the balance sheet impact of compressing Days Sales of Inventory (DSI) via stochastic S&OP.")

    s_col1, s_col2 = st.columns([1, 2])
    with s_col1:
        dsi_target_reduction = st.slider(
            "Target DSI Compression (Days):",
            min_value=1.0, max_value=15.0, value=4.0, step=0.5
        )
        sim_res = simulate_working_capital_unlock(c_data, target_dsi_reduction_days=dsi_target_reduction)

        st.markdown(f"""
        <div class="metric-card" style="margin-top:15px; border-left: 4px solid #10B981;">
            <div class="metric-label">One-Time Free Cash Flow Unlocked</div>
            <div class="metric-val" style="color:#059669;">${sim_res['free_cash_flow_unlocked_usd_m']:,.1f}M</div>
            <div style="font-size:0.85rem; color:#94A3B8; margin-top:5px;">Direct liquidity injected to balance sheet</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card" style="margin-top:15px; border-left: 4px solid #3B82F6;">
            <div class="metric-label">Annual P&L Carrying Cost Savings</div>
            <div class="metric-val" style="color:#2563EB;">${sim_res['annual_holding_cost_savings_usd_m']:,.2f}M / yr</div>
            <div style="font-size:0.85rem; color:#94A3B8; margin-top:5px;">Based on {sim_res['wacc_percent']}% corporate WACC</div>
        </div>
        """, unsafe_allow_html=True)

    with s_col2:
        # Before / After Inventory Waterfall Chart
        fig_waterfall = go.Figure(go.Waterfall(
            name="Working Capital",
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Current Inventory", f"-{dsi_target_reduction:.1f} Days DSI Optimization", "Optimized Inventory Target"],
            textposition="outside",
            text=[f"${sim_res['current_inventory_usd_m']:,.0f}M", f"-${sim_res['free_cash_flow_unlocked_usd_m']:,.1f}M", f"${sim_res['optimized_inventory_usd_m']:,.0f}M"],
            y=[sim_res['current_inventory_usd_m'], -sim_res['free_cash_flow_unlocked_usd_m'], sim_res['optimized_inventory_usd_m']],
            connector={"line": {"color": "#64748B"}},
            decreasing={"marker": {"color": "#10B981"}},
            increasing={"marker": {"color": "#EF4444"}},
            totals={"marker": {"color": "#0284C7"}}
        ))
        fig_waterfall.update_layout(
            title=f"{c_data['name']} Inventory Rationalization Waterfall ($M USD)",
            yaxis_title="USD ($M)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

    # 10-K Audit Memo Export
    with st.expander(f"📄 View & Export 10-K Operations Audit Memo for {c_data['name']}"):
        audit_memo = generate_10k_executive_audit_memo(c_data, sim_res)
        st.markdown(audit_memo)
        st.download_button(
            label=f"📥 Download {target_ticker} 10-K Board Memo (.md)",
            data=audit_memo,
            file_name=f"10K_Supply_Chain_Audit_{target_ticker}.md",
            mime="text/markdown"
        )

# -------------------------------------------------------------------------------------------------
# MODULE 4: EXECUTIVE OUTREACH & CAREER TOOLKIT
# -------------------------------------------------------------------------------------------------
elif app_mode == "4. Executive Outreach & Career Toolkit":
    st.markdown('<div class="main-header">Executive Outreach & Hiring Conversion Toolkit</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Turnkey assets to convert your project into direct interview invitations with VPs and Directors of Supply Chain.</div>', unsafe_allow_html=True)

    outreach_tab1, outreach_tab2, outreach_tab3 = st.tabs([
        "1. LinkedIn & Cold Email Outreach",
        "2. 2-Minute Loom Walkthrough Script",
        "3. Google XYZ Resume Bullets"
    ])

    with outreach_tab1:
        st.subheader("📬 High-Conversion Executive Pitch Scripts")
        st.markdown("""
        **Why this converts:** Directors and VPs receive dozens of generic messages like *"I am a recent graduate seeking opportunities..."*. 
        This message flips the dynamic: you are an **operations analyst presenting free intelligence on their actual 10-K financial challenges.**
        """)
        
        st.markdown("##### Template A: Targeting Emerson Electric (EMR)")
        st.code("""Subject: Ideas on Emerson's automation inventory velocity / WashU Olin SCM grad

Hi [First Name],

I've been following Emerson's focus on industrial automation post-transformation. In reviewing your latest 10-K, I noted your DSI currently sits at ~88 days, with significant capital tied up in discrete automation components.

As a recent Supply Chain Management graduate from WashU (Olin), I built a multi-echelon S&OP and nearshoring decision support engine to evaluate how stochastic lead-time buffers impact working capital. 

For Emerson, compressing DSI by just 4.0 days through dynamic supplier variance pacing could liberate ~$97M in one-time Free Cash Flow and save ~$8.2M annually in holding costs—without impacting 98% OTIF fill rates.

I recorded a 90-second interactive walkthrough of the model and balance sheet waterfall here: [Link to 90-sec Loom / Live App]

I'd welcome the chance to share this model with you or your materials planning team. Would you be open to a brief 10-minute conversation next Tuesday or Thursday?

Best regards,
[Your Name]
B.S. / M.S. Supply Chain Management | Washington University in St. Louis
[Phone] | [LinkedIn Profile] | [Live SCM Intelligence Platform Link]
""", language="markdown")

        st.markdown("##### Template B: Targeting Anheuser-Busch InBev (BUD)")
        st.code("""Subject: AB InBev SKU proliferation & safety stock analysis / WashU SCM

Hi [First Name],

Given AB InBev's operations hub here in St. Louis and your leadership in North American logistics, I wanted to share a brief working capital audit I recently completed.

While ABI maintains world-class negative working capital through payable management (DPO ~212 days), finished goods inventory has faced upward pressure from expanding craft and beyond-beer SKU portfolios. 

Using multi-echelon stochastic modeling, I evaluated how risk-pooling and lead-time volatility buffers can rationalise slow-moving (Z-tier) SKUs. Compressing ABI's inventory days by 3.5 days unlocks ~$261M in working capital liquidity.

Here is the live interactive tool and a 2-minute video walkthrough: [Link to Live App]

Would you be open to a 10-minute coffee or virtual chat to discuss how your team currently approaches stochastic safety buffers across your brewery DC network?

Warm regards,
[Your Name]
WashU Olin Supply Chain Management
""", language="markdown")

    with outreach_tab2:
        st.subheader("🎥 2-Minute Video Screen-Recording Script (Loom / YouTube Unlisted)")
        st.markdown("""
        Embed this 2-minute video at the top of your LinkedIn profile and attach it in email outreach.
        """)
        st.code("""[0:00 - 0:20] THE HOOK
"Hi everyone, my name is [Your Name], a recent Supply Chain Management graduate from Washington University in St. Louis. 
Most supply chain graduates look at inventory and sourcing through static textbook formulas. Today, I want to walk you through 
NexusSCM—an enterprise decision intelligence platform I engineered to solve the real-world trade-offs between geopolitical tariffs, 
lead-time volatility, and corporate working capital."

[0:20 - 0:50] MODULE 1: NEARSHORING & TOTAL LANDED COST
"First, let's look at global sourcing. A lot of companies look only at factory-gate purchase price. But when you factor in Section 301 
tariffs, 38 days of in-transit maritime financing, and the safety stock buffer required to absorb ocean port volatility, offshore 
margins evaporate. Here, with one slider, I simulate shifting from Shanghai to Monterrey, Mexico—demonstrating a compression of 32 transit 
days and unlocking $180,000 in working capital per SKU."

[0:50 - 1:25] MODULE 2: MULTI-ECHELON S&OP & THE EFFICIENT FRONTIER
"Next, in S&OP, executives constantly ask: 'Why can't we hit 99% OTIF without blowing up inventory?' 
This module plots the true non-linear Efficient Frontier. As you can see, jumping from 95% to 98% service level requires manageable cash, 
but hitting that final 1.5% causes working capital requirements to hockey-stick exponentially due to supplier lead-time variance. 
By centralizing safety buffers at the Central DC, we pool variance risk and cut decentralized carrying costs by 22%."

[1:25 - 1:50] MODULE 3: 10-K CORPORATE AUDIT
"Finally, I connected this operations engine directly to public SEC 10-K filings for companies like Emerson Electric and AB InBev. 
By modeling a conservative 4-day compression in Days Sales of Inventory, the engine computes the exact Free Cash Flow unlocked—over $97M 
in balance sheet liquidity for Emerson."

[1:50 - 2:00] THE CALL TO ACTION
"I'm actively seeking opportunities in S&OP planning, logistics strategy, and procurement analytics. 
You can test the live tool via the link below. Thank you for your time!"
""", language="markdown")

    with outreach_tab3:
        st.subheader("📄 Google XYZ Resume Bullets")
        st.markdown("""
        Replace generic bullet points on your resume with these verified, impact-driven statements:
        """)
        st.code("""• Engineered NexusSCM, an enterprise supply chain decision intelligence platform modeling multi-echelon stochastic safety stock and geopolitical Total Landed Cost (TLC) across 4 global sourcing corridors.
• Formulated dual-stochastic inventory optimization algorithms incorporating demand (σ_D) and supplier lead-time variance (σ_L); proved non-linear working capital scaling on the OTIF Efficient Frontier.
• Modeled multi-echelon risk pooling across Central and Regional Distribution Centers (CDC/RDC) utilizing the Square Root Law, identifying 22% reduction in decentralized safety stock holding capital.
• Reverse-engineered SEC Form 10-K filings for Fortune 500 enterprises (Emerson Electric, AB InBev, Boeing); built interactive Free Cash Flow unlock models illustrating how a 4-day DSI compression releases $97M+ in balance sheet liquidity.
• Built interactive executive simulation tool using Python (Streamlit, Pandas, SciPy, Plotly) delivering real-time tariff elasticity sensitivity, landed cost waterfalls, and automated board strategy memoranda.
""", language="markdown")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; font-size: 0.85rem;'>"
    "NexusSCM Decision Support Platform | Washington University in St. Louis — Olin Business School | Supply Chain & Operations Analytics"
    "</div>",
    unsafe_allow_html=True
)
