import asyncio
import ccxt.async_support as ccxt
import os
import json
import time
from config import config


class DivineHFTBot:

    def __init__(self):
        self.exchange = ccxt.binanceusdm({
            "apiKey": config.api_key,
            "secret": config.api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "future"},
        })
        self.exchange.set_sandbox_mode(True)

        self.symbol = config.symbol
        self.leverage = config.leverage

        self.maker_fee = 0.0002
        self.min_profit = config.min_profit
        self.max_position_usdt = 1_000_000

        self.state = "FLAT"
        self.order_id = None
        self.order_timestamp = None

        self.position_size = None
        self.entry_price = None

        self.history = []

        self.order_timeout = 2.0
        self.price_threshold = 0.0002

    async def get_prediction(self):
        await asyncio.sleep(0.1)
        return 60000, 60050

    async def calculate_position_size(self, price):
        balance = await self.exchange.fetch_balance()
        usdt = balance['USDT']['free']

        usable_cap = min(
            usdt,
            self.max_position_usdt / self.leverage,
            usdt * 0.5
        )

        notional = usable_cap * self.leverage
        qty = notional / price

        return float(self.exchange.amount_to_precision(self.symbol, qty))

    async def is_filled(self, order_id):
        order = await self.exchange.fetch_order(order_id, self.symbol)
        return order["status"] == "closed"

    async def cancel_order(self):
        try:
            await self.exchange.cancel_order(self.order_id, self.symbol)
        except:
            pass

    def is_timeout(self):
        return time.time() - self.order_timestamp > self.order_timeout

    async def run(self):
        print("Running FINAL HFT 10/10")
        await self.exchange.set_leverage(self.leverage, self.symbol)

        required_spread = (self.maker_fee * 2) + self.min_profit
        start = time.time()

        while time.time() - start < config.duration_seconds:

            Pmin, Pmax = await self.get_prediction()
            spread = (Pmax - Pmin) / Pmin

            if self.state == "FLAT":
                if spread >= required_spread:
                    qty = await self.calculate_position_size(Pmin)

                    try:
                        order = await self.exchange.create_limit_buy_order(
                            self.symbol, qty, Pmin
                        )
                        self.order_id = order["id"]
                        self.order_timestamp = time.time()
                        self.position_size = qty
                        self.entry_price = Pmin
                        self.state = "WAIT_BUY"

                        print(f"BUY placed @ {Pmin}")

                    except Exception as e:
                        print("BUY error:", e)

            elif self.state == "WAIT_BUY":

                if await self.is_filled(self.order_id):
                    print("BUY filled")
                    self.state = "LONG"

                elif self.is_timeout():
                    print("BUY timeout → cancel")
                    await self.cancel_order()
                    self.state = "FLAT"

                elif abs(Pmin - self.entry_price) / self.entry_price > self.price_threshold:
                    print("BUY price moved → replace")
                    await self.cancel_order()
                    self.state = "FLAT"

            elif self.state == "LONG":
                try:
                    order = await self.exchange.create_limit_sell_order(
                        self.symbol, self.position_size, Pmax
                    )
                    self.order_id = order["id"]
                    self.order_timestamp = time.time()
                    self.state = "WAIT_SELL"

                    print(f"SELL placed @ {Pmax}")

                except Exception as e:
                    print("SELL error:", e)

            elif self.state == "WAIT_SELL":

                if await self.is_filled(self.order_id):
                    exit_price = Pmax

                    profit = (
                        self.position_size * (exit_price - self.entry_price)
                        - 2 * self.maker_fee * self.position_size * self.entry_price
                    )

                    print(f"PROFIT: {profit:.2f}")

                    self.history.append({
                        "entry": self.entry_price,
                        "exit": exit_price,
                        "profit": profit,
                        "timestamp": time.time()
                    })

                    self.state = "FLAT"

                elif self.is_timeout():
                    print("SELL timeout → market close")

                    try:
                        await self.exchange.create_market_sell_order(
                            self.symbol, self.position_size
                        )
                    except:
                        pass

                    self.state = "FLAT"

            await asyncio.sleep(0.05)

        await self.exchange.close()

    async def save_history(self):
        os.makedirs(config.base_path, exist_ok=True)
        with open(os.path.join(config.base_path, "prod_history.json"), "w") as f:
            json.dump(self.history, f, indent=2)