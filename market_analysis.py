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
    # 仅保留日经225
    ticker_map = {
        "日经225 N225": "^N225"
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
    chan_analysis = data.pop("chan_analysis","")
    prompt = f"""
[硬性排版规则，严格遵守]
1. 板块之间用 --- 分割
2. 每个条目单独起段落，条目之间空一行
3. 禁止文字全部挤在一起，宽松排版
4. 全文控制在500字以内
5. 文末固定带上免责声明。

当日宏观事件：
{macro_info}

下面是标的上个交易日收盘数据：
{data}
缠论分型分析结果：{chan_analysis}

严格按下面模板输出：
# 📈 日股盘后报告
---
🌐 [宏观事件]
(宏观内容，优先日本央行、日元汇率相关信息)

---
📊 简述各标的涨跌情况：
(每条指数单独一行)

---
🔥盘面强弱解读：
(简短总结市场情绪)

---
📍缠论分型分析结果：{chan_analysis}，基于15分钟级别，说明压力/支撑参考：

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
    # Server酱 Turbo 官方标准API地址，SendKey嵌入URL
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    payload = {
        "title": title,
        "desp": content
    }
    try:
        resp = requests.post(url, data=payload, timeout=20)
        print(f"尝试接口 {url}，返回文本：{resp.text}")
        try:
            res = resp.json()
            if res.get("code",999) == 0:
                print("推送成功")
                return True
            else:
                # 业务层面报错（额度用尽、key无效），直接退出，不消耗额外额度
                print(f"返回业务错误，停止重试，保护额度")
                return False
        except:
            print(f"返回非JSON，推送失败")
            return False
    except Exception as e:
        print(f"请求异常：{str(e)}")
        return False

# ========== 主入口 ==========
if __name__ == "__main__":
    all_data = get_index_data()

    # 加载博查宏观新闻
    try:
        from skills.event_driven import get_macro_news
        macro_info = get_macro_news()
        all_data["macro_info"] = macro_info
    except Exception as e:
        all_data["macro_info"] = "暂无宏观资讯"

    # 加载缠论分析结果
    try:
        from skills.chan_theory import get_chan_analysis
        chan_result = get_chan_analysis(all_data)
        all_data["chan_analysis"] = chan_result
    except Exception as e:
        all_data["chan_analysis"] = "缠论分析获取失败"

    report_content = generate_analysis(all_data)
    send_wechat_report(title="日股盘后报告", content=report_content)
