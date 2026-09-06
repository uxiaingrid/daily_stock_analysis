import os
import requests
import yfinance as yf
from zhipuai import ZhipuAI

# 读取环境变量
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
SERVERCHAN_SENDKEY = os.getenv("SERVERCHAN_SENDKEY")

# 这里放 get_index_data() 函数

def generate_analysis(data):
    macro_info = data.pop("macro_info","")
    market_name = os.getenv("MARKET_NAME","")
    prompt = f"""
【硬性排版规则，严格遵守】
1. 采用公众号主流排版风格，段落间距1.5倍；使用Markdown语法+Emoji表情美化
2. 【宏观事件】为独立板块；板块之间用---分割线隔开
3. 每个条目单独起段落，条目之间空一行
4. 禁止文字全部挤在一起，不要紧凑排版
5. 全文控制在500字以内
6. 文末固定带上免责声明。

当日宏观事件：
{macro_info}

下面是标的上个交易日收盘数据：
{data}

严格按下面模板输出：
# 📈 {market_name}收盘报告
---
🌐【宏观事件】
（宏观内容，优先日本央行、日元汇率相关信息）

📊 简述各标的涨跌情况：

🔥盘面强弱解读：

📌结合附带的缠论分型信息（15分钟级别），简要说明各标的压力/支撑参考：

⚠️【本内容仅为数据复盘，不构成任何投资建议】
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
