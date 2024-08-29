import yfinance as yf
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import datetime

# 设置时间段：最近一年
end_date = datetime.datetime.today() - datetime.timedelta(days=100)
start_date = end_date - datetime.timedelta(days=3650)

tickers = ['KWEB', 'SPY', '600519.SS', '600036.SS']
weight = [0.05, 0.19, 0.017, 0.008]
weight_index = 0
sum = 0

for ticker in tickers:
    data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
    print(f"{ticker} data:")
    print(data.head())
    result = data * weight[weight_index]
    weight_index = weight_index + 1 
    print(result.head())
    sum = sum + result

# 绘制收盘价折线图
plt.figure(figsize=(10, 6))
plt.plot(sum, label=f'Asset Allocation')
plt.title(f'Asset Allocation vs Other Indexes')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.show()