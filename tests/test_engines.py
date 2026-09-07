"""
Unit Test Suite for NexusSCM Mathematical & Financial Engines
Verifies statistical models, total landed cost calculations, and 10-K financial ratios.
"""

import unittest
import math
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.landed_cost import norm_ppf, calculate_corridor_tlc, compare_sourcing_corridors
from core.inventory_optimizer import (
    calculate_stochastic_safety_stock,
    generate_efficient_frontier,
    simulate_multi_echelon_network
)
from core.financial_benchmarks import (
    compute_financial_ratios,
    simulate_working_capital_unlock,
    load_corporate_profiles
)
from core.report_generator import (
    generate_nearshoring_executive_memo,
    generate_10k_executive_audit_memo
)

class TestNexusSCM(unittest.TestCase):

    def test_norm_ppf_accuracy(self):
        """Verify normal quantile inverse CDF accuracy against standard statistical values."""
        self.assertAlmostEqual(norm_ppf(0.50), 0.0, places=3)
        self.assertAlmostEqual(norm_ppf(0.8413447), 1.0, places=2)
        self.assertAlmostEqual(norm_ppf(0.9772498), 2.0, places=2)
        self.assertAlmostEqual(norm_ppf(0.95), 1.645, places=2)
        self.assertAlmostEqual(norm_ppf(0.98), 2.054, places=2)

    def test_landed_cost_calculations(self):
        """Verify total landed cost, pipeline financing, and volatility buffer penalty."""
        tlc = calculate_corridor_tlc(
            base_purchase_cost=100.0,
            freight_cost=10.0,
            handling_drayage=2.0,
            tariff_rate=0.25,
            transit_time_days=30.0,
            lead_time_stdev_days=5.0,
            wacc=0.12,
            annual_volume=10000,
            service_level=0.98
        )
        self.assertEqual(tlc["base_purchase_cost"], 100.0)
        self.assertEqual(tlc["tariff_cost"], 25.0)
        self.assertEqual(tlc["duty_paid_purchase"], 125.0)
        self.assertEqual(tlc["logistics_cost"], 12.0)
        
        # Expected transit WC = 100 * 0.12 * (30/365) = 0.9863 -> 0.99
        self.assertAlmostEqual(tlc["transit_working_capital_cost"], 0.99, places=1)
        
        # Total landed cost should be >= base + tariff + freight
        self.assertGreater(tlc["total_landed_cost"], 137.0)
        self.assertGreater(tlc["annual_spend_usd"], 0)

    def test_sourcing_comparison(self):
        """Verify 4-corridor comparative scenario generation."""
        comp = compare_sourcing_corridors(
            part_name="Automotive Solenoid",
            annual_volume=20000,
            china_tariff=0.25,
            mexico_tariff=0.00
        )
        res = comp["corridor_results"]
        self.assertIn("China (Offshore Baseline)", res)
        self.assertIn("Mexico (Nearshore USMCA)", res)
        self.assertIn("US Domestic (Reshore)", res)
        self.assertIn("Vietnam (Alt Offshore)", res)
        
        # Mexico should have 0 tariff and shorter transit days
        self.assertEqual(res["Mexico (Nearshore USMCA)"]["tariff_cost"], 0.0)
        self.assertLess(res["Mexico (Nearshore USMCA)"]["transit_time_days"], 
                        res["China (Offshore Baseline)"]["transit_time_days"])

    def test_stochastic_safety_stock(self):
        """Verify dual-stochastic variance equation and non-linear service scaling."""
        low_sl = calculate_stochastic_safety_stock(
            annual_demand=10000,
            annual_demand_stdev=1500,
            lead_time_days=30,
            lead_time_stdev_days=4,
            service_level=0.90
        )
        high_sl = calculate_stochastic_safety_stock(
            annual_demand=10000,
            annual_demand_stdev=1500,
            lead_time_days=30,
            lead_time_stdev_days=4,
            service_level=0.99
        )
        self.assertGreater(high_sl["safety_stock_units"], low_sl["safety_stock_units"])
        self.assertGreater(high_sl["working_capital_locked_usd"], low_sl["working_capital_locked_usd"])

    def test_efficient_frontier_monotonicity(self):
        """Verify working capital rises monotonically on the Efficient Frontier."""
        frontier = generate_efficient_frontier(
            annual_demand=12000,
            annual_demand_stdev=2000,
            lead_time_days=45,
            lead_time_stdev_days=6,
            unit_cost=150.0
        )
        for i in range(1, len(frontier)):
            self.assertGreater(frontier[i]["working_capital_usd"], frontier[i-1]["working_capital_usd"])
            self.assertGreater(frontier[i]["service_level_percent"], frontier[i-1]["service_level_percent"])

    def test_multi_echelon_risk_pooling(self):
        """Verify Square Root law: Centralization lowers total safety stock vs decentralized nodes."""
        sample_skus = [
            {
                "sku_id": "SKU-1", "sku_name": "Valve", "annual_demand": 10000,
                "demand_stdev_annual": 2000, "unit_cost": 100.0,
                "supplier_lead_time_days": 30, "lead_time_stdev_days": 3
            }
        ]
        res = simulate_multi_echelon_network(sample_skus, num_rdcs=3)
        self.assertGreater(res["decentralized_capital_usd"], res["centralized_capital_usd"])
        self.assertGreater(res["total_working_capital_unlocked_usd"], 0)

    def test_financial_ratios(self):
        """Verify corporate 10-K financial ratio calculations (DSI, DSO, DPO, CCC)."""
        ratios = compute_financial_ratios(
            revenue_m=1000.0,
            cogs_m=600.0,
            inventory_m=100.0,
            ar_m=150.0,
            ap_m=80.0
        )
        # DSI = (100 / 600) * 365 = 60.83
        self.assertAlmostEqual(ratios["dsi_days"], 60.83, places=1)
        # DSO = (150 / 1000) * 365 = 54.75
        self.assertAlmostEqual(ratios["dso_days"], 54.75, places=1)
        # DPO = (80 / 600) * 365 = 48.67
        self.assertAlmostEqual(ratios["dpo_days"], 48.67, places=1)
        # CCC = 60.83 + 54.75 - 48.67 = 66.91
        self.assertAlmostEqual(ratios["ccc_days"], 66.91, places=1)

    def test_working_capital_unlock(self):
        """Verify Free Cash Flow unlock simulation on Emerson Electric profile."""
        profiles = load_corporate_profiles()
        emr = profiles["EMR"]
        sim = simulate_working_capital_unlock(emr, target_dsi_reduction_days=4.0)
        
        expected_daily_cogs = emr["metrics"]["cogs_usd_m"] / 365.0
        expected_fcf = 4.0 * expected_daily_cogs
        self.assertAlmostEqual(sim["free_cash_flow_unlocked_usd_m"], expected_fcf, places=1)
        self.assertGreater(sim["annual_holding_cost_savings_usd_m"], 0)

    def test_executive_memos(self):
        """Verify markdown executive report formatting."""
        comp = compare_sourcing_corridors("Test Valve", 10000)
        memo = generate_nearshoring_executive_memo(comp)
        self.assertIn("EXECUTIVE STRATEGY MEMORANDUM", memo)
        self.assertIn("QUANTIFIED FINANCIAL & OPERATIONAL IMPACT", memo)

if __name__ == "__main__":
    unittest.main()
