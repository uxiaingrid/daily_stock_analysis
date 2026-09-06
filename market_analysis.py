import os
import requests
import yfinance as yf
from zhipuai import ZhipuAI

# 读取环境变量
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
SERVERCHAN_SENDKEY = os.getenv("SERVERCHAN_SENDKEY")

def get_index_data():
    """获取上个交易日收盘数据"""
    result_data = {}
    ticker_map = {
        "日经225 N225": "^N225",
        "东证TOPIX": "^TOPX"
    }
    for name, ticker_code in ticker_map.items():
        ticker = yf.Ticker(ticker_code)
        hist = ticker.history(period="5d")
        if hist.empty:
            print(f"警告：{name} 无行情数据，跳过该指数")
            continue
        last_row = hist.iloc[-1]
        close_price = round(last_row["Close"],2)
        open_price = round(last_row["Open"],2)
        change = round(last_row["Close"] - last_row["Open"],2)
        change_pct = round(change / last_row["Open"] * 100, 2)
        result_data[name] = {
            "close": close_price,
            "open": open_price,
            "change": change,
            "change_pct": change_pct
        }
    return result_data

def generate_analysis(data):
    macro_info = data.pop("macro_info","")
    market_name = os.getenv("MARKET_NAME","")
    prompt = f"""
prompt = f"""
【硬性排版规则，严格遵守】
1. 板块之间用 --- 分割
2. 每个条目单独起段落，条目之间空一行
3. 禁止文字全部挤在一起，宽松排版
4. 全文控制在500字以内
5. 文末固定带上免责声明。

当日宏观事件：
{macro_info}

下面是标的上个交易日收盘数据：
{data}

严格按下面模板输出：
# 📈 {market_name}收盘报告
---
🌐【宏观事件】
(宏观内容，优先日本央行、日元汇率相关信息)

---
📊 简述各标的涨跌情况：
(每条指数单独一行)

---
🔥盘面强弱解读：
(简短总结市场情绪)

---
📍结合缠论分型信息（15分钟级别），说明各标的压力/支撑参考：
(每个标的压力、支撑分行书写)

⚠️免责声明：本内容仅为行情复盘研究，不构成任何投资建议
"""
    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content

def send_wechat_report(title, content):
    import requests
    sendkey = os.getenv("SERVERCHAN_SENDKEY")
    if not sendkey:
        print("SERVERCHAN_SENDKEY为空，推送终止")
        return False
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    payload = {
        "title": title,
        "desp": content
    }
    resp = requests.post(url, data=payload)
    print("Server酱返回结果：", resp.text)
    return resp.json()["code"] == 0

# ========== 主入口 ==========
if __name__ == "__main__":
    all_data = get_index_data()
    report_content = generate_analysis(all_data)
    # 调用微信推送
    send_wechat_report(title=f"{os.getenv('MARKET_NAME')}盘后报告", content=report_content)
