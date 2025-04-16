import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates # 用于更好地格式化日期轴

# --- 配置 ---
# 从用户获取股票代码
ticker_symbol = input("请输入股票代码 (例如: AAPL, MSFT, GOOG): ").strip().upper()
years_to_fetch = 15    # 获取多少年的数据

# --- 计算日期范围 ---
end_date = datetime.now()
# 近似计算15年前的日期，稍微往前一点以确保获取到第15个财年的数据
start_date_approx = end_date - timedelta(days=years_to_fetch * 365.25 + 60)

# --- 获取股票对象 ---
ticker = yf.Ticker(ticker_symbol)

# --- 获取年度财务数据 (损益表，需要EPS) ---
try:
    # .financials 通常返回年度数据，列是财年结束日期
    financials = ticker.financials
    if financials.empty:
        print(f"错误：无法获取 {ticker_symbol} 的年度财务数据。")
        exit()
    print("\n--- DEBUG: yfinance 返回的 financials 数据的列 (日期) ---")
    if not financials.empty:
        print(financials.columns)
    else:
        print("financials 数据为空")
    print("-----------------------------------------------------------\n")
    # 转置数据，使日期成为索引，方便按行查找项目
    financials_t = financials.T
    # 尝试获取 'Basic EPS' (基本每股收益)，如果不存在可能需要检查其他名称
    # yfinance 返回的列名可能会变化，常见的有 'Basic EPS', 'Diluted EPS'
    eps_col_name = None
    possible_eps_names = ['Basic EPS', 'Diluted EPS', 'Eps Basic', 'Eps Diluted']
    for name in possible_eps_names:
        if name in financials_t.columns:
            eps_col_name = name
            break

    if eps_col_name is None:
        print(f"错误：在财务数据中找不到EPS列。可用列：{financials_t.columns}")
        exit()

    # 提取EPS数据，并确保索引是日期时间格式
    eps = financials_t[eps_col_name].dropna() # 删除EPS缺失的年份
    eps.index = pd.to_datetime(eps.index)

    # 筛选出在计算出的近似开始日期之后的财年数据
    eps = eps[eps.index >= start_date_approx]
    # 确保我们有足够的数据点
    eps = eps.tail(years_to_fetch) # 精确获取最后 N 年的数据

    if eps.empty:
        print(f"错误：在指定时间范围内找不到 {ticker_symbol} 的EPS数据。")
        exit()

except Exception as e:
    print(f"获取财务数据时出错: {e}")
    exit()

# --- 获取历史股价数据 ---
# 获取覆盖所有EPS日期的每日收盘价
try:
    hist_prices = ticker.history(start=eps.index.min() - timedelta(days=30), # 比最早的EPS日期再往前一个月
                                 end=end_date,
                                 interval="1d") # 获取日线数据
    if hist_prices.empty:
        print(f"错误：无法获取 {ticker_symbol} 的历史股价数据。")
        exit()
    # 确保索引是 timezone-naive (或者与 EPS 索引一致)
    if hist_prices.index.tz is not None:
         hist_prices.index = hist_prices.index.tz_localize(None)

except Exception as e:
    print(f"获取历史股价时出错: {e}")
    exit()


# --- 计算年度市盈率 (P/E) ---
pe_ratios = {}
calculation_details = {} # 用于存储计算细节

for date, eps_value in eps.items():
    # 财年结束日期
    fiscal_year_end_date = date

    # 寻找财年结束日期当天或之前的最近一个交易日的收盘价
    try:
        # 选择在财年结束日期（包含当天）之前的所有价格数据
        relevant_prices = hist_prices[hist_prices.index <= fiscal_year_end_date]
        if not relevant_prices.empty:
            # 获取最后一行（即最接近 fiscal_year_end_date 的交易日）的收盘价
            closing_price = relevant_prices['Close'].iloc[-1]
            price_date = relevant_prices.index[-1] # 记录使用的股价日期

            # 计算 P/E，注意处理 EPS 为 0 或负数的情况
            if eps_value is not None and eps_value > 0:
                pe = closing_price / eps_value
                # 使用财年作为键（年份部分）
                pe_ratios[fiscal_year_end_date.year] = pe
                calculation_details[fiscal_year_end_date.year] = {
                    'Fiscal Year End': fiscal_year_end_date.strftime('%Y-%m-%d'),
                    'EPS': eps_value,
                    'Price Date': price_date.strftime('%Y-%m-%d'),
                    'Closing Price': closing_price,
                    'P/E Ratio': pe
                }
            else:
                # EPS <= 0, P/E 无意义或为负，这里选择不加入绘图数据
                pe_ratios[fiscal_year_end_date.year] = None # 标记为None
                calculation_details[fiscal_year_end_date.year] = {
                    'Fiscal Year End': fiscal_year_end_date.strftime('%Y-%m-%d'),
                    'EPS': eps_value,
                    'Price Date': price_date.strftime('%Y-%m-%d'),
                    'Closing Price': closing_price,
                    'P/E Ratio': 'N/A (EPS <= 0)'
                }
        else:
            print(f"警告：在 {fiscal_year_end_date.strftime('%Y-%m-%d')} 或之前找不到 {ticker_symbol} 的股价数据。")
            pe_ratios[fiscal_year_end_date.year] = None # 标记为None

    except Exception as e:
        print(f"计算 {fiscal_year_end_date.year} 年 P/E 时出错: {e}")
        pe_ratios[fiscal_year_end_date.year] = None # 标记为None


if not pe_ratios:
    print("错误：未能计算任何市盈率数据。")
    exit()

# --- 准备绘图数据 ---
# 将字典转换为 Pandas Series，便于绘图和处理
pe_series = pd.Series(pe_ratios).sort_index()
# 移除 P/E 为 None 的数据点，这些点不适合绘制在数值图上
pe_series_cleaned = pe_series.dropna()

# --- 打印计算明细 (可选) ---
print("\n--- 年度 P/E 计算明细 (基于财年结束数据) ---")
details_df = pd.DataFrame.from_dict(calculation_details, orient='index')
details_df.index.name = 'Year'
print(details_df)
print("----------------------------------------------")


# --- 绘制折线图 ---
plt.figure(figsize=(14, 7)) # 设置图形大小

plt.plot(pe_series_cleaned.index.astype(str), # X轴使用年份字符串
         pe_series_cleaned.values,
         marker='o',          # 在每个数据点上加圆圈标记
         linestyle='-',       # 使用实线连接
         color='royalblue'    # 设置线条颜色
        )

# 添加标题和标签
plt.title(f'{ticker_symbol} 过去 {years_to_fetch} 年市盈率(P/E)趋势 (基于财年结束数据)', fontsize=16)
plt.xlabel('年份', fontsize=12)
plt.ylabel('年度市盈率 (P/E Ratio)', fontsize=12)

# 设置 X 轴刻度为整数年，并旋转标签以防重叠
plt.xticks(rotation=45)

# 添加网格线
plt.grid(True, linestyle='--', alpha=0.6)

# 优化布局
plt.tight_layout()

# 显示图形
plt.show()

print(f"\n已生成 {ticker_symbol} 的市盈率趋势图。")