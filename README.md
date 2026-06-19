# Rolling-Window-Monte-Carlo-Segmented-Simulator---Personal-Adjustment-to-Master-Thesis

# Advanced Portfolio Performance Prediction via Rolling Window Monte Carlo Simulation

## Overview
This repository contains an advanced quantitative tool designed to assess and forecast investment portfolio performance. It serves as an upgraded version of a Master's thesis simulation, implementing a **Rolling Window Monte Carlo** approach with a **self-adjusting drift** mechanism. By dynamically shifting across time blocks, the model inherently adapts to changing market regimes and volatility states.

The analysis is executed in Python, utilizing pre-calculated logarithmic returns to ensure strict mathematical consistency across all simulation stages.

---

## Methodology & Core Enhancements

### 1. Asset Selection & Modern Portfolio Theory (MPT)
The model processes a universe of assets (e.g., from the WIG30 index) and constructs three distinct strategic portfolios using advanced optimization frameworks (`PyPortfolioOpt`):
* **Risk / Max Sharpe Portfolio:** Optimizes the risk-adjusted return using a Ledoit-Wolf shrinkage covariance matrix to guarantee mathematical convexity.
* **Moderate / Inverse Variance Portfolio:** Allocates weights inversely proportional to asset variance for stable, balanced diversification.
* **Least Risky / Hierarchical Risk Parity (HRP) Portfolio:** Utilizes graph theory and machine learning-driven clustering to minimize risk without relying on expected returns.

### 2. The Segmented Simulator (Rolling Window & Self-Adjusting Drift)
Unlike traditional geometric Brownian motion models that apply a single static drift, this simulator introduces a **segmented, regime-aware resampling framework**:
* **Rolling Windows:** The historical 300-day dataset of log returns is segmented into distinct temporal blocks (e.g., Oldest, Middle, and Recent market regimes).
* **Self-Adjusting Drift:** The simulation dynamically samples from these independent blocks to build 10,000 future paths over a 90-day horizon. This allows the simulation to factor in structural market shifts, changing trends, and evolving volatility clusters rather than assuming market conditions remain constant.

---

## Project Structure

The project has been refactored from a monolithic script into modular, specialized components to prevent calculations from overlapping or failing:
* **`Quant Trading Project.py` (Main):** The central execution script handling data ingestion, portfolio optimization, simulation, and risk reporting.
* **`MCS_MAX.py` / `MCS_MIN.py` / `MCS_OPT.py`:** Individual dedicated scripts isolating the Monte Carlo engines for each specific portfolio strategy.
* **`Raw_Version.py`:** The original, non-refactored monolithic baseline representing the first development iteration.

---

## Quantitative Risk Audit & Outputs

Upon completing 10,000 iterations, the engine generates individual interactive charts charting the expected trajectories and stress zones, alongside a professional risk report delivered directly to the terminal:

```text
=============================================
      QUANTITATIVE RISK AUDIT
=============================================
[RISK (SHARPE)]
 > Expected 90-day Return: +11.45%
 > Value at Risk (95%):    15.20% loss
 > Expected Shortfall (CVaR): 19.85% loss
-------------------------
[MODERATE]
 > Expected 90-day Return: +7.29%
 > Value at Risk (95%):    12.10% loss
 > Expected Shortfall (CVaR): 16.32% loss
-------------------------
[LEAST RISKY (HRP)]
 > Expected 90-day Return: +4.15%
 > Value at Risk (95%):    6.40% loss
 > Expected Shortfall (CVaR): 8.90% loss
-------------------------
