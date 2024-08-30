import yfinance as yf
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import datetime

def popAndPad(list, pop, pad):
    series_length = len(list)
    # print(f"series_length: {series_length}")
    cloned_series = list.copy()
    i = 0
    
    while True:
        assert i >= 0
        assert pop >= 1
        updated_index = i + (pop * 365)
        assert updated_index >= 365
        if updated_index >= series_length - 1:
            break
        # print(f"updated_index: {updated_index}")
        # assert updated_index >= 365
        cloned_series.iloc[updated_index] = list.iloc[i + ((pop - 1) * 365)]
        i = i + 1
    
    for i in range(pop - 1):
        for j in range(365):
            cloned_series.iloc[i * 365 + j] = pad
        
    return cloned_series

year = 10
end_date = datetime.datetime.today()
start_date = end_date - datetime.timedelta(days=365 * year)

sp500 = yf.download('VOO', start=start_date, end=end_date)['Adj Close']
sp500_first = sp500.iloc[0]

cn300 = yf.download('ASHR', start=start_date, end=end_date)['Adj Close']
cn300_first = cn300.iloc[0]

tickers = ['KWEB', 'VOO', '600519.SS', '600036.SS', 'GLD', 'ASHR', '511260.SS', 'AAPL', 'TSLA', 'TCEHY', 'API', 'TLT', 'SGOV', 'VGIT']
weight = [0.03, 0.21, 0.017, 0.008, 0.03, 0.015, 0.01, 0.015, 0.01, 0.015, 0.05, 0.07, 0.09, 0.02]
assert len(tickers) == len(weight)
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

# print("cd data:")
cd_raw = yf.download('^TNX', start=start_date, end=end_date)['Adj Close']
cd_raw = (cd_raw + 100) / 100
# print(cd_raw.head())
# TODO 债劵的分红

cd_year = int(len(cd_raw) / 365)
cd = 1
# cd = cd_raw
for i in range(1, cd_year):
    # print(f"i: {i}")
    cd = cd * popAndPad(cd_raw, i, 1)
cd_result = cd * 0.23
print(f"cd: {cd.head()}")
real_estate = 0.18
# 假设房地产和货币基金不涨不跌
# 绘制收盘价折线图
sum = sum + real_estate + cd_result
sp500 = sp500 / sp500_first
cn300 = cn300 / cn300_first

last_element = sum.iloc[-20] ** (1 / year)
print(f'资产配置年化收益率:{(last_element - 1) * 100:.2f}%')
sp500_last_element = sp500.iloc[-20] ** (1 / year)
print(f'标普500年化收益率:{(sp500_last_element - 1) * 100:.2f}%')
cn300_last_element = cn300.iloc[-20] ** (1 / year)
print(f'沪深300年化收益率:{(cn300_last_element - 1) * 100:.2f}%')
cd_last_element = cd.iloc[-20] ** (1 / year)
print(f'定期存款年化收益率:{(cd_last_element - 1) * 100:.2f}%')

plt.figure(figsize=(10, 6))
plt.plot(sum, label=f'Asset Allocation')
plt.plot(sp500, label=f'S&P 500')
plt.plot(cn300, label=f'CN 300')
plt.plot(cd, label=f'Pure CD')
plt.title(f'Asset Allocation vs Other Indexes')
plt.xlabel('Date')
plt.ylabel('Percentage')
plt.legend()
plt.grid(True)
plt.show()
