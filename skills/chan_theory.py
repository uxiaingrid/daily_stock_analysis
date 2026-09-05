import yfinance as yf
import pandas as pd

def get_chanlun_analysis(symbol, period="1mo", interval="1d"):
    """
    缠论简易分析，识别顶底分型、支撑压力，输出文本
    symbol：标的代码 ^SPX / ^NDX / ^DJI
    interval 默认日线；如需15分钟线改为 interval="15m"
    """
    df = yf.download(symbol, period=period, interval=interval)
    if len(df) < 10:
        return "K线数据不足，无法进行缠论分析"
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    # 简易分型判断
    def is_ding_fenxing(i):
        return high[i] > high[i-1] and high[i] > high[i+1] and low[i] > low[i-1] and low[i] > low[i+1]
    def is_di_fenxing(i):
        return low[i] < low[i-1] and low[i] < low[i+1] and high[i] < high[i-1] and high[i] < high[i+1]

    ding_list = []
    di_list = []
    for i in range(2, len(df)-2):
        if is_ding_fenxing(i):
            ding_list.append(high.iloc[i])
        if is_di_fenxing(i):
            di_list.append(low.iloc[i])

    latest_price = close.iloc[-1]
    resistance = ding_list[-2:] if len(ding_list)>=2 else [latest_price*1.02, latest_price*1.04]
    support = di_list[-2:] if len(di_list)>=2 else [latest_price*0.98, latest_price*0.96]

    text = f"""
【缠论技术分析】
标的：{symbol}，周期：{interval}
最新价格：{latest_price:.2f}
近期压力位：{resistance}
近期支撑位：{support}
顶分型价格序列：{ding_list[-3:]}
底分型价格序列：{di_list[-3:]}
说明：本模块仅做分型识别，不构成买卖建议
"""
    return text
