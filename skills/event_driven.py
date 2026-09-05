import os
import requests

def get_macro_news():
    """调用博查API，查询美股宏观新闻、非农、CPI、美联储相关资讯"""
    api_key = os.getenv("BOCHA_API_KEY")
    if not api_key:
        return "未读取BOCHA_API_KEY，无法获取宏观新闻"
    url = "https://api.bochaai.com/v1/web-search"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"}
    payload = {
        "query":"美股 美联储 CPI 非农 最新市场影响",
        "summary": True,
        "count": 5
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        res = resp.json()
        lst = res.get("data",{}).get("webPages",{}).get("value",[])
        if not lst:
            return "近期无重大宏观财经事件"
        out = "【宏观催化新闻】\n"
        for item in lst:
            out += f"- {item.get('name')}：{item.get('summary')}\n"
        return out
    except Exception as e:
        return f"新闻接口异常：{str(e)}"
