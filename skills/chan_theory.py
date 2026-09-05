import yfinance as yf
import pandas as pd

def get_chanlun_analysis(symbol, period="1mo", interval="1d"):
    """
    缠论简易分析，识别顶底分型、支撑压力，输出文本
    symbol: 标的代码 ^GSPC / ^NDX / ^DJI
    interval 默认日线；如需15分钟线改为 interval="15m"
    """
    df = yf.download(symbol, period=period, interval=interval)
    # 压平多层列名
    df.columns = df.columns.get_level_values(0)
    
    if len(df) < 10:
        return "K线数据不足，无法进行缠论分析"
    
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    # 简易分型判断
    def is_ding_fenxing(i):
        return high.iloc[i] > high.iloc[i-1] and high.iloc[i] > high.iloc[i+1] and low.iloc[i] > low.iloc[i-1] and low.iloc[i] > low.iloc[i+1]

    def is_di_fenxing(i):
        return low.iloc[i] < low.iloc[i-1] and low.iloc[i] < low.iloc[i+1] and high.iloc[i] < high.iloc[i-1] and high.iloc[i] < high.iloc[i+1]

    ding_list = []
    di_list = []
    for i in range(2, len(df)-2):
        if is_ding_fenxing(i):
            ding_list.append(high.iloc[i])
        if is_di_fenxing(i):
            di_list.append(low.iloc[i])

    latest_price = close.iloc[-1]
    # 取最近2个分型作为压力/支撑，不足则自动估算
    resistance = ding_list[-2:] if len(ding_list)>=2 else [latest_price*1.02, latest_price*1.04]
    support = di_list[-2:] if len(di_list)>=2 else [latest_price*0.98, latest_price*0.96]

    result_text = f"""
标的：{symbol}，最新价格：{latest_price:.2f}
识别到最近顶分型（压力位）：{resistance}
识别到最近底分型（支撑位）：{support}
说明：仅简易分型计算，不含完整笔、线段、中枢，仅供参考，不构成投资建议。
"""
    return result_text
