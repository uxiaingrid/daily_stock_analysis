import os
import requests

def get_macro_news():
    """调用博查API，查询日股相关宏观新闻：日本央行、日元、日债、美联储对日经/东证影响"""
    api_key = os.getenv("BOCHA_API_KEY")
    if not api_key:
        return "未读取BOCHA_API_KEY，无法获取宏观新闻"
    url = "https://api.bochaai.com/v1/web-search"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"}
    payload = {
        "query":"日本央行 日元汇率 日债 美联储政策 对日经225、东证TOPIX的市场影响，最新宏观资讯",
        "summary": True,
        "count": 5
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        res = resp.json()
        lst = res.get("data",{}).get("webPages",{}).get("value",[])
        if not lst:
            return "暂无相关宏观资讯"
        contents = []
        for item in lst:
            s = item.get("summary","")
            if s:
                contents.append(s)
        full_text = "\n".join(contents)
        return full_text[:800]
    except Exception as e:
        return f"宏观新闻获取异常：{str(e)}"
