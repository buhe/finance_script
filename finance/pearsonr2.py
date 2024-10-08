import yfinance as yf
from scipy.stats import pearsonr
import datetime

# 设置时间段：最近一年
end_date = datetime.datetime.today() - datetime.timedelta(days=100)
start_date = end_date - datetime.timedelta(days=3650)

# 下载纳斯达克金龙中国指数（HXC）和标普500指数（^GSPC）的数据
hxc = yf.download('AAPL', start=start_date, end=end_date)['Adj Close']
sp500 = yf.download('SPY', start=start_date, end=end_date)['Adj Close']

# 计算每日收益率
hxc_returns = hxc.pct_change().dropna()
sp500_returns = sp500.pct_change().dropna()

# 计算相关性系数
correlation, _ = pearsonr(hxc_returns, sp500_returns)

print(f"苹果（AAPL）与标普500指数过去10年的相关性系数为: {correlation:.4f}")