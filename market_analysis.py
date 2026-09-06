def generate_analysis(data):
    macro_info = data.pop("macro_info","")
    market_name = os.getenv("MARKET_NAME","")
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

严格按下面模板输出：
# 📈 {market_name}收盘报告
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
