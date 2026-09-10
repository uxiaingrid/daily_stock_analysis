import os
import requests
import yfinance as yf
from zhipuai import ZhipuAI

# 读取环境变量
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
SERVERCHAN_SENDKEY = os.getenv("SERVERCHAN_SENDKEY")
BOCHA_API_KEY = os.getenv("BOCHA_API_KEY")

def bocha_search(query):
    url = "https://api.bochaai.com/v1/web-search"
    headers = {"Authorization": f"Bearer {BOCHA_API_KEY}", "Content-Type":"application/json"}
    payload = {
        "query": query,
        "summary": True,
        "count":5
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        data = resp.json()
        res_list = []
        for item in data.get("data",{}).get("webPages",{}).get("value",[]):
            res_list.append(item.get("summary",""))
        return "\n".join(res_list)
    except Exception as e:
        print(f"博查搜索出错:{e}")
        return ""

def get_macro_news():
    """获取日股近24小时宏观新闻，强制过滤旧新闻"""
    raw_news = bocha_search("日本股市 日经225 日本宏观经济 日元汇率，只检索最近24小时新闻，排除超过24小时的历史旧资讯，不要过往月份旧新闻")
    if not raw_news.strip():
        return "近一日无重大日本宏观新闻"
    return raw_news

def get_index_data():
    """获取上个交易日收盘数据，日经225 + 东证TOPIX(1306.T ETF替代)，修复涨跌幅计算"""
    result_data = {}
    ticker_map = {
        "日经225 N225": "^N225",
        "东证TOPIX 1306.T": "1306.T"
    }
    for name, ticker_code in ticker_map.items():
        ticker = yf.Ticker(ticker_code)
        hist = ticker.history(period="5d")
        if hist.empty or len(hist) < 2:
            print(f"警告：{name} 无行情数据，跳过该指数")
            continue
        last_close = hist.iloc[-1]["Close"]
        prev_close = hist.iloc[-2]["Close"]
        close_price = round(last_close,2)
        change = round(last_close - prev_close,2)
        change_pct = round(change / prev_close * 100, 2)
        result_data[name] = {
            "close": close_price,
            "change": change,
            "change_pct": change_pct
        }
    return result_data

def generate_analysis_report(raw_data):
    macro_info = "暂无宏观资讯"
    try:
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
4. 文末放置免责声明

【重要硬性约束】
1. 只使用近1‑3个交易日的日股相关新闻；禁止输出数周前历史旧资讯；**禁止输出本周累计涨跌幅统计**。
2. 行情只描述当日收盘涨跌，宏观事件逻辑要和当日盘面保持一致，不能矛盾。
3. 不要额外增加标题，严格使用模板内已有的标题文本，禁止重复生成标题。

宏观事件信息：
{macro_info}

标的行情数据：
{raw_data}

缠论分型分析结果：{chan_analysis}

输出模板：
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

# 主入口（已加入无有效行情则跳过推送防护）
if __name__ == "__main__":
    market_data = get_index_data()
    if not market_data:
        print("无有效日股行情数据，跳过推送")
    else:
        report_text = generate_analysis_report(market_data)
        send_wechat_report("日股盘后报告", report_text)
