import os
import json
import matplotlib.pyplot as plt
from src.utils import generate_tick, calculate_order, calc_net_profit


class Simulator:
    """Offline симулятор HFT стратегии (математическая модель)"""

    def __init__(self, capital, leverage, ticks_count=864000):
        self.capital = capital
        self.leverage = leverage
        self.ticks_count = ticks_count
        self.history = []
        self.maker_fee = 0.0002
        self.max_position_usdt = 1_000_000

    def run(self):
        required_spread = (self.maker_fee * 2) + 0.0001

        for _ in range(self.ticks_count):
            Pmin, Pmax = generate_tick()
            spread = (Pmax - Pmin) / Pmin

            if spread >= required_spread:
                Q, pos_notional = calculate_order(Pmin, Pmax, self.capital, self.leverage, self.max_position_usdt)
                net_profit = calc_net_profit(Q, pos_notional, Pmin, Pmax, self.maker_fee, self.capital)
                self.capital += net_profit
            else:
                net_profit = 0

            self.history.append({
                "Pmin": Pmin,
                "Pmax": Pmax,
                "capital": self.capital,
                "net_profit": net_profit
            })

    def save_history(self, base_path="results"):
        os.makedirs(base_path, exist_ok=True)
        with open(os.path.join(base_path, "sim_history.json"), "w") as f:
            json.dump(self.history, f, indent=2)

        equity = [item["capital"] for item in self.history]
        plt.figure(figsize=(10, 5))
        plt.plot(equity, label="Equity curve (x100 Leverage)", color="blue")
        plt.xlabel("Tick (100ms)")
        plt.ylabel("Capital ($)")
        plt.yscale('log')
        plt.title(f"Offline HFT Simulation (Cap: ${self.max_position_usdt:,})")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.legend()
        plt.savefig(os.path.join(base_path, "equity_curve.png"))
        plt.close()