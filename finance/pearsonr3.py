import yfinance as yf
from scipy.stats import pearsonr
import datetime

# 设置时间段：最近一年
end_date = datetime.datetime.today() - datetime.timedelta(days=100)
start_date = end_date - datetime.timedelta(days=3650)

# 下载纳斯达克金龙中国指数（HXC）和标普500指数（^GSPC）的数据
hxc = yf.download('ASHR', start=start_date, end=end_date)['Adj Close']
sp500 = yf.download('SPY', start=start_date, end=end_date)['Adj Close']
tlt = yf.download('TLT', start=start_date, end=end_date)['Adj Close']
gld = yf.download('GLD', start=start_date, end=end_date)['Adj Close']

# 计算每日收益率
hxc_returns = hxc.pct_change().dropna()
sp500_returns = sp500.pct_change().dropna()
tlt_returns = tlt.pct_change().dropna()
gld_returns = gld.pct_change().dropna()

# 计算相关性系数
correlation, _ = pearsonr(hxc_returns, sp500_returns)
correlation2, _ = pearsonr(hxc_returns, gld_returns)
correlation3, _ = pearsonr(tlt_returns, sp500_returns)
correlation4, _ = pearsonr(gld_returns, sp500_returns)

print(f"沪深300与标普500指数过去10年的相关性系数为: {correlation:.4f}")
print(f"沪深300与黄金指数过去10年的相关性系数为: {correlation2:.4f}")
print(f"TLT与标普500指数过去10年的相关性系数为: {correlation3:.4f}")
print(f"黄金指数与标普500指数过去10年的相关性系数为: {correlation4:.4f}")