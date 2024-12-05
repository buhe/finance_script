import yfinance as yf

# 下载中证红利指数数据
data = yf.download("ASHR", start="2020-01-01", end="2020-12-01")
print(data)