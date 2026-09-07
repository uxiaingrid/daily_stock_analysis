import yfinance as yf

def get_chan_analysis(raw_data):
    """缠论分析：只取东证ETF 1306.T，15分钟K线，仅保留最近2组顶底分型+结构总结"""
    ticker_code = "1306.T"
    try:
        ticker = yf.Ticker(ticker_code)
        df = ticker.history(period="5d", interval="15m")
        if df.empty:
            return f"{ticker_code} 无法获取15分钟K线，缠论分析失败"

        high_list = df["High"].tolist()
        low_list = df["Low"].tolist()
        top_list = []
        bottom_list = []

        for i in range(2, len(high_list)-2):
            h_mid = high_list[i]
            h_left1, h_left2 = high_list[i-1], high_list[i-2]
            h_right1, h_right2 = high_list[i+1], high_list[i+2]
            l_mid = low_list[i]
            l_left1, l_left2 = low_list[i-1], low_list[i-2]
            l_right1, l_right2 = low_list[i+1], low_list[i+2]
            # 顶分型
            if h_mid > h_left1 and h_mid > h_left2 and h_mid > h_right1 and h_mid > h_right2:
                top_list.append(round(h_mid,2))
            # 底分型
            if l_mid < l_left1 and l_mid < l_left2 and l_mid < l_right1 and l_mid < l_right2:
                bottom_list.append(round(l_mid,2))

        # 取最后2个，只保留最近信号
        recent_top = top_list[-2:] if len(top_list)>=2 else top_list
        recent_bottom = bottom_list[-2:] if len(bottom_list)>=2 else bottom_list

        # 结构简单判断
        if len(recent_top)>=1 and len(recent_bottom)>=1:
            if recent_top[-1] > recent_bottom[-1]:
                trend_desc = "当前15分钟级别处于震荡上行结构"
            else:
                trend_desc = "当前15分钟级别处于震荡下行结构"
        else:
            trend_desc = "当前15分钟无明确单边方向，区间震荡"

        top_str = "、".join([str(p) for p in recent_top]) if recent_top else "无"
        bot_str = "、".join([str(p) for p in recent_bottom]) if recent_bottom else "无"
        res_text = f"标的：东证TOPIX ETF(1306.T)，15分钟级别缠论：最近顶分型{top_str}；最近底分型{bot_str}，{trend_desc}"
        return res_text[:300]
    except Exception as e:
        return f"缠论分析获取失败：{str(e)}"
