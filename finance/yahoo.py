import yfinance as yf
yf.enable_debug_mode()
stock_a = yf.download(['AAPL', 'TSLA', 'MSFT'], start='2016-01-01', end='2017-12-31')
print(stock_a)