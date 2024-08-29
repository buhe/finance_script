import yfinance as yf
from scipy.stats import pearsonr
import datetime

# 设置时间段：最近一年
end_date = datetime.datetime.today() - datetime.timedelta(days=100)
start_date = end_date - datetime.timedelta(days=3650)

tickers = ['KWEB', 'SPY']
weight = [0.05, 0.19]
weight_index = 0

for ticker in tickers:
    data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
    print(data.head())
    result = data * weight[weight_index]
    weight_index = weight_index + 1 
    print(result.head())