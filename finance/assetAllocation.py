import yfinance as yf
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import datetime

# 设置时间段：最近一年
end_date = datetime.datetime.today()
start_date = end_date - datetime.timedelta(days=3650)

sp500 = yf.download('SPY', start=start_date, end=end_date)['Adj Close']
sp500_first = sp500.iloc[0]
tickers = ['KWEB', 'SPY', '600519.SS', '600036.SS', 'GLD', 'ASHR', '511260.SS', '^TNX', 'AAPL', 'TSLA', 'TCEHY', 'API', 'SPY', 'TLT', 'SGOV', 'VGIT']
weight = [0.05, 0.19, 0.017, 0.008, 0.03, 0.015, 0.01, 0.23, 0.01 * 2, 0.01, 0.01, 0.05, 0.19, 0.07, 0.09, 0.02]
weight_index = 0
sum = 0

for ticker in tickers:
    data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
    first = data.iloc[0]
    print(f"{ticker} data:")
    # print(first) # 打印第一个日期的收盘价
    # print(data.head())
    # print(data.head() / first)
    result = data / first * weight[weight_index]
    weight_index = weight_index + 1 
    print(result.head())
    sum = sum + result

# 绘制收盘价折线图
plt.figure(figsize=(10, 6))
plt.plot(sum, label=f'Asset Allocation')
plt.plot(sp500 / sp500_first, label=f'S&P 500')
plt.title(f'Asset Allocation vs Other Indexes')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.show()