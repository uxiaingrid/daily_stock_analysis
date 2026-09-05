import os
import requests
import yfinance as yf
from zhipuai import ZhipuAI
import importlib.util

def load_skills():
    skill_names_raw = os.getenv("AGENT_SKILLS","")
    skill_names = skill_names_raw.split(",")
    skill_modules = {}
    for name in skill_names:
        name = name.strip()
        if not name:
            continue
        file_path = f"skills/{name}.py"
        if os.path.exists(file_path):
            spec = importlib.util.spec_from_file_location(name, file_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            skill_modules[name] = mod
    return skill_modules

ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
SERVERCHAN_SENDKEY = os.getenv("SERVERCHAN_SENDKEY")

ticker_map = {
    "标普500 SPX": "^GSPC",
    "道指 DJI": "^DJI",
    "纳指综合 IXIC": "^IXIC",
    "纳指100 NDX": "^NDX",
    "费城半导体 SOX": "^SOX"
}

def get_index_data():
    skills = load_skills()
    # ========= 博查宏观新闻：只调用1次 =========
    macro_event = ""
    if "event_driven" in skills:
        try:
            macro_event = skills["event_driven"].get_macro_news()
            print(f"====DEBUG 宏观新闻返回值====\n{macro_event}")
        except Exception as e:
            macro_event = f"【宏观新闻异常】{str(e)}"
            print(f"====DEBUG 宏观报错====\n{e}")

    result_data = {}
    for name, ticker_code in ticker_map.items():
        ticker = yf.Ticker(ticker_code)
        hist = ticker.history(period="5d")
        latest = hist.iloc[-1]
        prev = hist.iloc[-2]
        close_price = round(latest["Close"],2)
        change = round(latest["Close"] - prev["Close"],2)
        change_pct = round((latest["Close"] - prev["Close"])/prev["Close"]*100,2)

        # ========== 缠论调用：SOX特殊处理 ==========
        chan_result = ""
        if "chan_theory" in skills:
            try:
                if ticker_code == "^SOX":
                    chan_result = skills["chan_theory"].get_chanlun_analysis(ticker_code, period="30d", interval="1d")
                else:
                    chan_result = skills["chan_theory"].get_chanlun_analysis(ticker_code, period="5d", interval="15m")
            except Exception as e:
                chan_result = f"【缠论获取失败】{str(e)}"
        # ========================================

        result_data[name] = {
            "收盘": close_price,
            "涨跌": change,
            "涨跌幅%": change_pct,
            "缠论分型": chan_result
        }
    # 附加宏观新闻
    result_data["macro_info"] = macro_event
    return result_data

def generate_analysis(data):
    macro_info = data.pop("macro_info","")
    prompt = f"""
【硬性规则：生成的报告开头必须单独保留【宏观事件】板块，不允许省略、合并、删除这段内容】
当日美股宏观事件：
{macro_info}

下面是美股五大指数上个交易日收盘数据：
{data}

输出格式严格按照下面模板：
美股收盘报告
【宏观事件】
（这里写宏观新闻总结）
1、简述各指数涨跌情况：
2、盘面强弱简单解读，重点留意费城半导体表现：
3、结合附带的缠论分型信息（15分钟级别，SOX为日线级别），简要说明各指数压力/支撑参考：

全文控制在500字以内。
⚠️ 强制在文末标注：【本内容仅为数据复盘，不构成任何投资建议】
"""
    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content

def serverchan_send(title, content, sendkey):
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    data = {
        "title": title,
        "desp": content
    }
    try:
        res = requests.post(url, data=data, timeout=10)
        print(res.json())
    except Exception as e:
        print(f"Server酱推送异常: {e}")

if __name__ == "__main__":
    try:
        index_data = get_index_data()
        report = generate_analysis(index_data)
        serverchan_send("美股收盘报告", report, SERVERCHAN_SENDKEY)
        print("✅ 任务执行完毕")
    except Exception as e:
        print(f"主程序整体异常：{e}")
