import asyncio
from config import config
from src.strategy import DivineHFTBot
from src.simulator import Simulator

async def run_prod():
    bot = DivineHFTBot()
    await bot.run()
    await bot.save_history()

def run_offline():
    sim = Simulator(capital=config.capital, leverage=config.leverage, ticks_count=864000)
    sim.run()
    sim.save_history(base_path=config.base_path)
    print(f"Total simulated profit: {sim.capital - config.capital:.2f} USD")
    print(f"Results saved to {config.base_path}/ directory")

if __name__ == "__main__":
    if config.mode == "prod":
        print("Running in PROD mode (Sandbox ccxt)")
        asyncio.run(run_prod())
    else:
        print("Running in OFFLINE mode (Synthetic math simulation)")
        run_offline()