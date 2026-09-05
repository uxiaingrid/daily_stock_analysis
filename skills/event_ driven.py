import os
import requests

def get_macro_news():
    """Tavily 搜索美股宏观新闻，替代博查"""
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    if not TAVILY_API_KEY:
        return "Tavily密钥未配置"
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "query": "美股 美联储 最新宏观新闻，非农，CPI，利率，地缘消息",
        "search_depth": "basic",
        "max_results":3
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        res_json = resp.json()
        if res_json.get("results") is None:
            return f"Tavily调用失败：{res_json}"
        news_text = ""
        for item in res_json["results"]:
            news_text += f"- {item['content']}\n"
        return news_text
    except Exception as e:
        return f"新闻抓取异常：{str(e)}"
