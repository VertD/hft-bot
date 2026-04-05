"""Configuration loader for Divine Predictor HFT bot"""
import yaml

class Config:
    def __init__(self, cfg_dict):
        self.api_key = cfg_dict.get("api_key", "")
        self.api_secret = cfg_dict.get("api_secret", "")
        self.symbol = cfg_dict["symbol"]
        self.leverage = cfg_dict["leverage"]
        self.capital = cfg_dict["capital"]
        self.min_profit = cfg_dict["min_profit"]
        self.duration_seconds = cfg_dict["duration_seconds"]
        self.base_path = cfg_dict.get("base_path", "results")
        self.mode = cfg_dict.get("mode", "offline")

with open("config.yaml", "r") as f:
    config = Config(yaml.safe_load(f))