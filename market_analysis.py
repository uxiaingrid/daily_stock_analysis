import os
import requests
import yfinance as yf
from zhipuai import ZhipuAI

# 读取密钥，仅从github secrets读取
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")

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
        hist = ticker.history(period="5d")
        latest = hist.iloc[-1]
        prev = hist.iloc[-2]
        close_price = round(latest["Close"],2)
        change = round(latest["Close"] - prev["Close"],2)
        change_pct = round((latest["Close"] - prev["Close"])/prev["Close"]*100, 2)
        result_data[name] = {
            "收盘": close_price,
            "涨跌": change,
            "涨跌幅%": change_pct
        }
    return result_data

def generate_analysis(data):
    prompt = f"""
下面是美股五大指数上个交易日收盘数据：
{data}
生成简短盘后行情分析：
1、简述各指数涨跌情况
2、盘面强弱简单解读，重点留意费城半导体表现
全文控制在300字以内。
⚠️ 强制在文末标注：【本内容仅为数据复盘，不构成任何投资建议】
"""
    client = ZhipuAI(api_key=ZHIPU_API_KEY)
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content

def send_wechat_push(content):
    url = "http://www.pushplus.plus/send"
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": "美股盘后复盘报告",
        "content": content
    }
    res = requests.post(url, json=payload)
    print("PushPlus推送返回：", res.text)

if __name__ == "__main__":
    index_data = get_index_data()
    report = generate_analysis(index_data)
    send_wechat_push(report)
    print("✅ 任务执行完毕")
