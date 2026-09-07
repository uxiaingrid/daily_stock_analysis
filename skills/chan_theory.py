import yfinance as yf

def get_chan_analysis(raw_data):
    """缠论分析：只取东证ETF 1306.T，15分钟K线"""
    ticker_code = "1306.T"
    try:
        # 拉取15分钟K线，最近5个交易日
        ticker = yf.Ticker(ticker_code)
        df = ticker.history(period="5d", interval="15m")
        if df.empty:
            return f"{ticker_code} 无法获取15分钟K线，缠论分析失败"

        # 简易缠论分型识别
        high_list = df["High"].tolist()
        low_list = df["Low"].tolist()
        fenxing_msg = ""
        for i in range(2, len(high_list)-2):
            h_mid = high_list[i]
            h_left1, h_left2 = high_list[i-1], high_list[i-2]
            h_right1, h_right2 = high_list[i+1], high_list[i+2]
            l_mid = low_list[i]
            l_left1, l_left2 = low_list[i-1], low_list[i-2]
            l_right1, l_right2 = low_list[i+1], low_list[i+2]
            # 顶分型
            if h_mid > h_left1 and h_mid > h_left2 and h_mid > h_right1 and h_mid > h_right2:
                fenxing_msg += f"顶分型，价格{h_mid:.2f}；"
            # 底分型
            if l_mid < l_left1 and l_mid < l_left2 and l_mid < l_right1 and l_mid < l_right2:
                fenxing_msg += f"底分型，价格{l_mid:.2f}；"

        if fenxing_msg == "":
            fenxing_msg = "近期无明显顶底分型"
        res_text = f"标的：东证TOPIX ETF(1306.T)，15分钟级别缠论：{fenxing_msg}"
        return res_text[:400]
    except Exception as e:
        return f"缠论分析获取失败：{str(e)}"
