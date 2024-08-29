import yfinance as yf
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import datetime

# 设置时间段：最近10年
end_date = datetime.datetime.today()
start_date = end_date - datetime.timedelta(days=3650)

sp500 = yf.download('SPY', start=start_date, end=end_date)['Adj Close']
sp500_first = sp500.iloc[0]

cn300 = yf.download('ASHR', start=start_date, end=end_date)['Adj Close']
cn300_first = cn300.iloc[0]

tickers = ['KWEB', 'SPY', '600519.SS', '600036.SS', 'GLD', 'ASHR', '511260.SS', 'AAPL', 'TSLA', 'TCEHY', 'API', 'SPY', 'TLT', 'SGOV', 'VGIT']
weight = [0.05, 0.19, 0.017, 0.008, 0.03, 0.015, 0.01, 0.01 * 2, 0.01, 0.01, 0.05, 0.19, 0.07, 0.09, 0.02]
weight_index = 0
sum = 0

for ticker in tickers:
    data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
    first = data.iloc[0]
    # print(f"{ticker} data:")
    # print(first) # 打印第一个日期的收盘价
    # print(data.head())
    # print(data.head() / first)
    result = data / first * weight[weight_index]
    weight_index = weight_index + 1 
    # print(result.head())
    sum = sum + result

print("cd data:")
cd_raw = yf.download('^TNX', start=start_date, end=end_date)['Adj Close']
cd_raw = (((cd_raw + 100) / 100) ** 1)
# TODO 债劵的分红
# TODO cd 的复利
cd = cd_raw ** 10 * 0.23


real_estate = 0.18
# 假设房地产和货币基金不涨不跌
# 绘制收盘价折线图
plt.figure(figsize=(10, 6))
plt.plot(sum + real_estate + cd, label=f'Asset Allocation')
plt.plot(sp500 / sp500_first, label=f'S&P 500')
plt.plot(cn300 / cn300_first, label=f'CN 300')
plt.title(f'Asset Allocation vs Other Indexes')
plt.xlabel('Date')
plt.ylabel('Percentage')
plt.legend()
plt.grid(True)
plt.show()