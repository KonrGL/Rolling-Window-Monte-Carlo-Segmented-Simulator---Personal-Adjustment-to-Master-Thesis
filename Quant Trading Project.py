import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from pypfopt import HRPOpt, EfficientFrontier, risk_models, expected_returns


def calculate_portfolio_drei(file_path):
    # Load Pre-calculated Log Returns
    returns_df = pd.read_excel(file_path, index_col=0, parse_dates=True).dropna()
    data_300 = returns_df.tail(300)

    # Correlation Heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(data_300.corr(), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Asset Correlation Heatmap (300-Day History)')
    plt.show()

    # 1. Max Sharpe (Risk)
    mu = expected_returns.mean_historical_return(data_300, returns_data=True)
    S = risk_models.sample_cov(data_300, returns_data=True)
    ef = EfficientFrontier(mu, S)
    try:
        ef.max_sharpe()
        weights_risk = dict(ef.clean_weights())
    except:
        weights_risk = dict(ef.min_volatility())

    # 2. Inverse Variance (Moderate)
    variances = data_300.var()
    inv_var = 1.0 / variances
    weights_mod = dict(inv_var / inv_var.sum())

    # 3. HRP (Least Risky)
    hrp = HRPOpt(data_300)
    weights_least = dict(hrp.optimize())


    print("\n" + "=" * 45)
    print("      INITIAL PORTFOLIO COMPOSITION")
    print("=" * 45)

    all_weights = pd.DataFrame({
        'Risk (Sharpe)': weights_risk,
        'Moderate (InvVar)': weights_mod,
        'Least Risky (HRP)': weights_least
    })

    print(all_weights.fillna(0).applymap(lambda x: f"{x:.2%}" if x > 0 else "-"))
    print("=" * 45 + "\n")

    return {
        'Risk': weights_risk,
        'Moderate': weights_mod,
        'Least Risky': weights_least,
        'data': data_300
    }


def run_segmented_simulation(portfolio_results):
    data_300 = portfolio_results['data']
    weights_dict = {
        'Risk': portfolio_results['Risk'],
        'Moderate': portfolio_results['Moderate'],
        'Least Risky': portfolio_results['Least Risky']
    }

    block1 = data_300.iloc[0:100]  # Oldest
    block2 = data_300.iloc[100:200]  # Middle
    block3 = data_300.iloc[200:300]  # Recent

    simulation_final = {}

    for p_name, weights in weights_dict.items():
        print(f" > Simulating {p_name} Strategy...")
        w_vector = np.array([weights[t] for t in data_300.columns])
        all_paths = []

        for _ in range(10000):
            ch1 = block3.sample(n=30, replace=True).values
            ch2 = block2.sample(n=30, replace=True).values
            ch3 = block1.sample(n=30, replace=True).values

            full_period = np.vstack([ch1, ch2, ch3])
            daily_returns = np.dot(full_period, w_vector)

            path = 100 * np.exp(np.cumsum(daily_returns))
            path = np.insert(path, 0, 100)
            all_paths.append(path)

        all_paths = np.array(all_paths)
        reduced_paths = all_paths.reshape(500, 20, 91).mean(axis=1)

        simulation_final[p_name] = {
            'raw': all_paths,
            'smooth': reduced_paths
        }

    print("✅ Simulation Complete for all portfolios.")
    return simulation_final


def plot_results_with_corridors(simulation_final):
    colors = {'Risk': '#e74c3c', 'Moderate': '#f39c12', 'Least Risky': '#27ae60'}
    days = np.arange(91)

    for p_name, data in simulation_final.items():
        plt.figure(figsize=(12, 7))  # Dedicated window for each portfolio
        raw = data['raw']
        smooth = data['smooth']
        color = colors[p_name]

        median = np.percentile(raw, 50, axis=0)
        upper_95 = np.percentile(raw, 95, axis=0)
        lower_5 = np.percentile(raw, 5, axis=0)
        upper_75 = np.percentile(raw, 75, axis=0)
        lower_25 = np.percentile(raw, 25, axis=0)

        for i in range(len(smooth)):
            plt.plot(days, smooth[i], color=color, alpha=0.04, linewidth=0.8)

        plt.fill_between(days, lower_5, upper_95, color=color, alpha=0.1,
                         label=f'Stress Zone (5-95%): {lower_5[-1]:.1f} - {upper_95[-1]:.1f}')
        plt.fill_between(days, lower_25, upper_75, color=color, alpha=0.2,
                         label=f'Expected Zone (25-75%): {lower_25[-1]:.1f} - {upper_75[-1]:.1f}')

        plt.plot(days, median, color=color, linewidth=3, label=f'Median Path: {median[-1]:.1f}')

        plt.axhline(100, color='black', linestyle='--', alpha=0.6)

        plt.axvline(30, color='grey', linestyle=':', alpha=0.4, label='Regime Shift (30/60d)')
        plt.axvline(60, color='grey', linestyle=':', alpha=0.4)

        plt.title(f"90-Day Forecast: {p_name.upper()} Strategy", fontsize=16, fontweight='bold')
        plt.xlabel("Days into Future", fontsize=12)
        plt.ylabel("Portfolio Value (Base 100)", fontsize=12)
        plt.legend(loc='upper left')
        plt.grid(alpha=0.2)
        plt.tight_layout()

        plt.show()


def run_risk_audit(simulation_final):
    print("\n" + "=" * 45)
    print("      QUANTITATIVE RISK AUDIT")
    print("=" * 45)

    for p_name, data in simulation_final.items():
        final_values = data['raw'][:, -1]
        median_return = np.percentile(final_values, 50) - 100
        var_95 = 100 - np.percentile(final_values, 5)
        worst_5_percent = final_values[final_values <= np.percentile(final_values, 5)]
        cvar = 100 - worst_5_percent.mean()

        print(f"[{p_name.upper()}]")
        print(f" > Expected 90-day Return: {median_return:+.2f}%")
        print(f" > Value at Risk (95%):    {var_95:.2f}% loss")
        print(f" > Expected Shortfall (CVaR): {cvar:.2f}% loss")
        print("-" * 25)


if __name__ == "__main__":
    print("\n--- QUANT PORTFOLIO TERMINAL ---")
    raw_input = input("Please enter the file directory and name (e.g., C:/Users/data.xlsx): ").strip()
    file_path = raw_input.replace('"', '').replace("'", "")

    if os.path.exists(file_path):
        try:
            # 1. Weights & Composition
            portfolio_results = calculate_portfolio_drei(file_path)

            # 2. Simulations
            simulation_output = run_segmented_simulation(portfolio_results)

            # 3. Graph
            plot_results_with_corridors(simulation_output)

            # 4. Audit
            run_risk_audit(simulation_output)

            print("\nAnalysis complete.")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
    else:
        print(f"❌ Error: File not found at '{file_path}'.")

#TO calculate final investment value you have to consult "final value" position on graph and calculate:
#FV = Simulation Result/100 * invested amount