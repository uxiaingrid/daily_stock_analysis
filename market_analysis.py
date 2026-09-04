import os
import requests
import yfinance as yf
from zhipuai import ZhipuAI

# 读取密钥，仅从github secrets读取
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
SERVERCHAN_SENDKEY = os.getenv("SERVERCHAN_SENDKEY")

# ===== 5个指数代码，完整清单 =====
ticker_map = {
    "标普500 SPX": "^GSPC",
    "道指 DJI": "^DJI",
    "纳指综合 IXIC": "^IXIC",
    "纳指100 NDX": "^NDX",
    "费城半导体 SOX": "^SOX"
}

def get_index_data():
    """获取上个交易日收盘数据"""
    result_data = {}
    for name, ticker_code in ticker_map.items():
        ticker = yf.Ticker(ticker_code)
        hist = ticker.history(period="5d")...
