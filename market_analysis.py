import os
import requests
import yfinance as yf
from zhipuai import ZhipuAI

# 读取环境变量
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
SERVERCHAN_SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
BOCHA_API_KEY = os.getenv("BOCHA_API_KEY")

def get_index_data():
    """获取上个交易日收盘数据，日经225 + 东证TOPIX(1306.T ETF替代)"""
    result_data = {}
    ticker_map = {
        "日经225 N225": "^N225",
        "东证TOPIX 1306.T": "1306.T"
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

def generate_analysis_report(raw_data):
    macro_info = "暂无宏观资讯"
    try:
        from skills.event_driven import get_macro_news
        macro_info = get_macro_news()
    except Exception as e:
        macro_info = "博查API密钥未配置"

    chan_analysis = "缠论分析获取失败，基于15分钟级别，说明压力/支撑参考："
    try:
        from skills.chan_theory import get_chan_analysis
        chan_analysis = get_chan_analysis(raw_data)
    except Exception as e:
        chan_analysis = "缠论分析获取失败，基于15分钟级别，说明压力/支撑参考："

    prompt = f"""
【排版规则，严格遵守】
1. 板块之间使用 --- 分割
2. 段落宽松，不要挤成一团
3. 全文控制在500字以内
4. 文末固定免责声明

宏观事件信息：
{macro_info}

标的行情数据：
{raw_data}

缠论分型分析结果：{chan_analysis}

输出模板：
# 📈 日股盘后报告
---
🌐 宏观事件

---
📊 简述各标的涨跌情况：
（逐个列出指数行情）

---
🔥盘面强弱解读：
简短总结市场情绪

---
📍缠论分型分析结果：{chan_analysis}

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
    try:
        resp = requests.post(url, data=payload, timeout=20)
        print(f"请求返回：{resp.text}")
        try:
            res = resp.json()
            if res.get("code",999) == 0:
                print("推送成功")
                return True
            else:
                print(f"推送业务失败：{res}")
                return False
        except:
            print("返回非JSON，推送失败")
            return False
    except Exception as e:
        print(f"推送请求异常：{str(e)}")
        return False

# 主入口
if __name__ == "__main__":
    market_data = get_index_data()
    report_text = generate_analysis_report(market_data)
    send_wechat_report("日股盘后报告", report_text)
