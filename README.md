# NexusSCM: Enterprise Supply Chain Decision Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-7.0-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Institution](https://img.shields.io/badge/Institution-WashU%20Olin%20SCM-BA0C2F.svg)](https://olin.wustl.edu/)

**NexusSCM** is a board-ready executive decision support workbench engineered to solve high-stakes supply chain trade-offs:
1. **Geopolitical Nearshoring & Total Landed Cost (TLC):** Section 301 tariffs, ocean shipping lead-time volatility, pipeline financing, and Scope 3 carbon.
2. **Multi-Echelon Stochastic Inventory & S&OP:** Non-linear *Efficient Frontier* trade-offs between Customer OTIF Service Level (%) and Total Working Capital ($M).
3. **Corporate 10-K Working Capital Audit:** Audited balance sheet analytics for Fortune 500 enterprises (Emerson Electric, AB InBev, Boeing, Bayer) to quantify Free Cash Flow (FCF) releases from DSI compression.

---

## 🏛️ System Architecture

```
nexus_scm_platform/
├── app.py                      # Main Streamlit application with 4 executive modules
├── requirements.txt            # Python dependencies (streamlit, pandas, numpy, scipy, plotly)
├── README.md                   # Comprehensive technical documentation & deployment guide
├── core/
│   ├── landed_cost.py          # Geopolitical sourcing & Total Landed Cost (TLC) engine
│   ├── inventory_optimizer.py  # Multi-echelon stochastic safety stock & S&OP optimizer
│   ├── financial_benchmarks.py # 10-K financial ratio parser & Free Cash Flow unlock simulator
│   └── report_generator.py     # Executive board memo and audit report generator
├── data/
│   ├── corporate_10k_data.json # Audited balance sheet & inventory data (EMR, BUD, BA, BAYN)
│   ├── lane_benchmarks.csv     # Logistics corridor benchmarks (China, Mexico, Vietnam, US)
│   └── sample_skus.csv         # Enterprise multi-echelon SKU master catalog
├── tests/
│   └── test_engines.py         # Automated unit test suite verifying mathematical correctness
└── executive_toolkit/
    ├── outreach_templates.md   # Cold email & LinkedIn scripts targeting VPs/Directors of SCM
    ├── loom_script.md          # 2-minute video presentation script for recruiters
    └── resume_bullets.md       # Google XYZ formula bullet points for ATS optimization
```

---

## 📐 Mathematical Formulations

### 1. Total Landed Cost (TLC) with Volatility Buffer Penalty
Standard procurement models only evaluate purchase price and direct freight. NexusSCM models true economic landed cost:

$$\text{TLC} = P_{\text{base}} + \text{Tariff} + \text{Freight} + \text{Drayage} + \text{WCC}_{\text{transit}} + \text{BufferPenalty}$$

Where:
- $\text{Tariff} = P_{\text{base}} \times \tau_{\text{corridor}}$
- $\text{In-Transit Working Capital Financing: } \text{WCC}_{\text{transit}} = P_{\text{base}} \times \text{WACC} \times \left(\frac{L_{\text{transit}}}{365}\right)$
- $\text{Volatility Buffer Penalty: } \text{BufferPenalty} = \frac{Z \cdot \sigma_L \cdot P_{\text{base}} \cdot \text{WACC}}{365}$

### 2. Dual-Stochastic Multi-Echelon Safety Stock
Incorporates simultaneous variance in customer demand ($\sigma_D$) and supplier transit lead time ($\sigma_L$):

$$\sigma_{\text{DDLT}} = \sqrt{L \cdot \sigma_D^2 + D_{\text{daily}}^2 \cdot \sigma_L^2}$$

$$\text{Safety Stock (Units)} = Z(\text{OTIF}) \times \sigma_{\text{DDLT}}$$

$$\text{Reorder Point (ROP)} = (D_{\text{daily}} \times L) + \text{Safety Stock}$$

### 3. Corporate 10-K Free Cash Flow Release
When supply chain process improvements compress Days Sales of Inventory ($DSI$) by $\Delta DSI$ days:

$$\text{Daily COGS} = \frac{\text{COGS}_{\text{annual}}}{365}$$

$$\Delta \text{Cash (One-Time Free Cash Flow)} = \Delta DSI \times \text{Daily COGS}$$

$$\text{Recurring Annual P&L Savings} = \Delta \text{Cash} \times \text{WACC}$$

---

## 🚀 Quickstart & Local Execution

### 1. Environment Setup
```bash
# Clone or navigate to the repository
cd nexus_scm_platform

# Create virtual environment and activate
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Automated Verification Tests
```bash
python3 -m unittest tests/test_engines.py
```
All 9 unit tests verify mathematical precision, standard normal distributions, and balance sheet reconciliation.

### 3. Launch the Executive Platform
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 2-Minute Free Cloud Deployment (Streamlit Community Cloud)

To share this live tool with hiring managers and include a clickable URL on your resume:
1. Create a free GitHub repository (e.g. `nexus-scm-platform`) and push this codebase.
2. Sign in to [share.streamlit.io](https://share.streamlit.io) using your GitHub account.
3. Click **"New App"**, select your repository, set the main file to `app.py`, and click **Deploy**.
4. You will receive a permanent public URL (e.g., `https://yourname-scm-intelligence.streamlit.app`) to embed directly on your resume, LinkedIn, and email outreach.

---

## 👨‍💼 Author
**Washington University in St. Louis (WashU)**  
Olin Business School — Supply Chain & Operations Analytics  
*Designed for corporate supply chain leaders seeking data-driven operations strategy.*
