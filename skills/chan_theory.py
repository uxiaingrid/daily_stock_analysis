import yfinance as yf
import pandas as pd

def get_chanlun_analysis(symbol, period="5d", interval="15m"):
    """
    缠论简易分析，识别顶底分型、支撑压力
    symbol:指数代码
    period:时间跨度
    interval:K线周期，15m=15分钟线
    """
    try:
        df = yf.download(symbol, period=period, interval=interval)
        # 压平多层列名
        df.columns = df.columns.get_level_values(0)
        if len(df) < 10:
            return "K线数据不足，无法计算分型"
        
        close = df["Close"]
        high = df["High"]
        low = df["Low"]

        # 简易分型判断函数
        def is_ding_fx(i):
            return high.iloc[i] > high.iloc[i-1] and high.iloc[i] > high.iloc[i+1] and low.iloc[i] > low.iloc[i-1] and low.iloc[i] > low.iloc[i+1]
        def is_di_fx(i):
            return low.iloc[i] < low.iloc[i-1] and low.iloc[i] < low.iloc[i+1] and high.iloc[i] < high.iloc[i-1] and high.iloc[i] < high.iloc[i+1]

        ding_list = []
        di_list = []
        for i in range(2, len(df)-2):
            if is_ding_fx(i):
                ding_list.append(high.iloc[i])
            if is_di_fx(i):
                di_list.append(low.iloc[i])

        latest_price = close.iloc[-1]
        resistance = ding_list[-2:] if len(ding_list)>=2 else [round(latest_price*1.02,2), round(latest_price*1.04,2)]
        support = di_list[-2:] if len(di_list)>=2 else [round(latest_price*0.98,2), round(latest_price*0.96,2)]

        res_text = f"""标的:{symbol},最新价:{latest_price:.2f}
最近顶分型压力:{resistance}
最近底分型支撑:{support}
仅简易分型，不含笔/线段/中枢，仅供复盘"""
        return res_text
    except Exception as err:
        return f"【chan_theory异常】{str(err)}"
