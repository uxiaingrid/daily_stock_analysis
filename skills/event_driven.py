import os
import requests

def get_macro_news():
    """获取宏观财经新闻"""
    BOCHA_API_KEY = os.getenv("BOCHA_API_KEY")
    if not BOCHA_API_KEY:
        return "博查API密钥未配置"
    url = "https://api.bochaai.com/v1/web-search"
    headers = {"Authorization": f"Bearer {BOCHA_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "query":"日本央行 日元汇率 日债 美联储政策 对日经225、东证TOPIX的市场影响，最新宏观资讯",
        "summary": True,
        "count": 5
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        res_json = resp.json()
        if res_json.get("code") != 200:
            return f"博查调用失败：{res_json.get('msg')}"
        items = res_json["data"]["webPages"]["value"]
        news_text = ""
        for item in items:
            news_text += f"- {item['summary']}\n"
        return news_text
    except Exception as e:
        return f"新闻抓取异常：{str(e)}"
