import yfinance as yf
import time
import os
import sys
from datetime import datetime
import winsound # 用于播放提示音

# 检查是否安装了必要的库
try:
    import pandas as pd
except ImportError:
    print("pandas库未安装，请使用以下命令安装：")
    print("pip install pandas openpyxl")
    exit(1)

# 设置显示进度的函数
def print_progress(current, total, ticker="", prefix="进度", suffix="完成", length=50):
    """显示进度条"""
    percent = float(current) * 100 / total
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix}: |{bar}| {percent:.1f}% {suffix} {ticker}')
    sys.stdout.flush()
    if current == total:
        print()

def get_sp500_tickers():
    """
    获取标普500成分股的股票代码列表
    """
    # 使用yfinance获取标普500成分股列表
    # 可以通过下载^GSPC的信息来获取
    sp500 = yf.Ticker("^GSPC")
    
    try:
        # 尝试获取标普500的成分股
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        sp500_table = tables[0]  # 第一个表格通常是成分股列表
        tickers = sp500_table["Symbol"].tolist()
        return tickers
    except Exception as e:
        print(f"\n获取 500 列表出错: {e}")
        # 如果上面的方法失败，使用备选方法
        # 下载标普500 ETF (SPY)的前几个大权重股作为示例
        # 在实际应用中，可以考虑使用其他数据源获取完整列表
        return ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'GOOG', 'BRK-B', 'UNH', 'JPM', 'XOM', 'JNJ', 'V', 'PG', 'MA']

def get_financial_metrics(ticker):
    """
    获取单个股票的财务指标
    """
    try:
        stock = yf.Ticker(ticker)
        
        # 获取财务信息
        info = stock.info
        
        # 计算毛利率 (Gross Margin)
        gross_margin = info.get('grossMargins', None)
        
        # 获取市盈率 (PE Ratio)
        pe_ratio = info.get('trailingPE', None)
        
        # 计算净资产收益率 (ROE)
        roe = info.get('returnOnEquity', None)

        # 获取市值
        market_cap = info.get('marketCap', None)

        # 获取股息率 (年化)
        dividend_yield = info.get('dividendYield', None) # TTM dividend yield
        # 修正：如果股息率看起来像百分比（>1），则转换为小数
        if dividend_yield is not None and isinstance(dividend_yield, (int, float)):
        #  and dividend_yield > 1:
            dividend_yield /= 100
        # 获取年化股息 (每股)
        dividend_rate = info.get('dividendRate', None) # Forward annual dividend rate
        if dividend_rate is None:
            dividend_rate = info.get('trailingAnnualDividendRate', None) # TTM annual dividend rate

        # 获取流通股数
        shares_outstanding = info.get('sharesOutstanding', None)

        # 计算总股息支付额 (近似)
        total_dividend_paid = None
        if dividend_rate is not None and shares_outstanding is not None:
            total_dividend_paid = dividend_rate * shares_outstanding
        # elif dividend_yield is not None and market_cap is not None:
        #     # 如果没有每股股息，用股息率和市值估算
        #     # 注意：这里的 dividend_yield 已经是修正后的小数值
        #     total_dividend_paid = dividend_yield * market_cap

        # 获取现金流量表和资产负债表数据
        equity_multiplier = None
        buyback_amount = None
        profit_growth_y1 = None
        profit_growth_y2 = None
        profit_growth_y3 = None
        asset_liability_coverage = None # 初始化资产负债覆盖率
        debt_ratio = None # 初始化有息负债率
        short_term_debt_cash_ratio = None # 初始化短期负债与现金比率
        try:
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow # 获取现金流量表
            financials = stock.financials # 获取年度损益表

            # 计算权益乘数 和 Over 比率
            if not balance_sheet.empty:
                latest_bs = balance_sheet.iloc[:, 0]
                total_assets = latest_bs.get('Total Assets', None)
                total_equity = latest_bs.get('Total Stockholder Equity', None)
                if total_equity is None: total_equity = latest_bs.get('Stockholders Equity', None)
                if total_equity is None: total_equity = latest_bs.get('Total Equity Gross Minority Interest', None)

                # 获取现金及现金等价物
                cash_and_equivalents = latest_bs.get('Cash And Cash Equivalents', None)
                if cash_and_equivalents is None: cash_and_equivalents = latest_bs.get('Cash', None) # 备用键
                if cash_and_equivalents is None: cash_and_equivalents = latest_bs.get('Cash And Equivalents', None) # 另一个备用键
                if pd.isnull(cash_and_equivalents): cash_and_equivalents = 0 # 处理 NaN

                # 计算权益乘数
                if total_assets is not None and total_equity is not None and total_equity != 0:
                    equity_multiplier = total_assets / total_equity

                # 计算资产负债覆盖率 (总资产 / 流动负债) - 保留旧代码以防万一，但不再使用该变量
                # current_liabilities = latest_bs.get('Total Current Liabilities', None)
                # if current_liabilities is None: current_liabilities = latest_bs.get('Current Liabilities', None) # 备用键名
                # if total_assets is not None and current_liabilities is not None and current_liabilities != 0:
                #     asset_liability_coverage = total_assets / current_liabilities # 旧代码

                # 计算有息负债率
                total_liabilities = latest_bs.get('Total Liabilities Net Minority Interest', None)
                if total_liabilities is None: total_liabilities = latest_bs.get('Total Liabilities', None) # 备用键

                short_term_debt = latest_bs.get('Current Debt', 0) # 如果没有则视为0
                if short_term_debt is None: short_term_debt = latest_bs.get('Short Term Debt', 0) # 备用键
                if pd.isnull(short_term_debt): short_term_debt = 0 # 处理 NaN

                long_term_debt = latest_bs.get('Long Term Debt', 0) # 如果没有则视为0
                if pd.isnull(long_term_debt): long_term_debt = 0 # 处理 NaN

                short_term_debt_cash_ratio = None # 初始化短期负债与现金比率
                if total_liabilities is not None and total_liabilities != 0:
                    interest_bearing_debt = short_term_debt + long_term_debt
                    debt_ratio = interest_bearing_debt / total_liabilities

                # 计算短期负债与现金等价物比例
                if cash_and_equivalents is not None and cash_and_equivalents != 0:
                    # short_term_debt 已经在前面获取并处理了 NaN
                    short_term_debt_cash_ratio = short_term_debt / cash_and_equivalents
            # 计算回购额
            if not cashflow.empty:
                latest_cf = cashflow.iloc[:, 0] # 获取最新一期数据
                repurchase_key = None
                possible_buyback_keys = [
                    'Repurchase Of Stock', 
                    'Repurchase Of Capital Stock', 
                    'Repurchase/retirement Of Stock'
                ]
                for key in possible_buyback_keys:
                    if key in latest_cf.index:
                        repurchase_key = key
                        break
                
                if repurchase_key:
                    buyback_value = latest_cf.get(repurchase_key, 0)
                    buyback_amount = abs(buyback_value) if pd.notnull(buyback_value) else 0
                else:
                    buyback_amount = 0
            else:
                 buyback_amount = 0

            # 计算利润增长率
            if not financials.empty and financials.shape[1] >= 4: # 确保至少有4年的数据
                # 尝试获取净利润，yfinance的键名可能变化
                net_income_key = None
                possible_income_keys = [
                    'Net Income',
                    'Net Income Applicable To Common Shares',
                    'Net Income From Continuing Ops'
                ]
                for key in possible_income_keys:
                    if key in financials.index:
                        net_income_key = key
                        break
                
                if net_income_key:
                    # 获取最近四年的净利润 (yfinance列通常是时间倒序)
                    ni_y0 = financials.loc[net_income_key].iloc[0] # 最近一年
                    ni_y1 = financials.loc[net_income_key].iloc[1]
                    ni_y2 = financials.loc[net_income_key].iloc[2]
                    ni_y3 = financials.loc[net_income_key].iloc[3] # 第四年前

                    # 计算增长率，处理分母为0或负数的情况
                    if pd.notnull(ni_y0) and pd.notnull(ni_y1) and ni_y1 > 0:
                        profit_growth_y1 = (ni_y0 / ni_y1) - 1
                    if pd.notnull(ni_y1) and pd.notnull(ni_y2) and ni_y2 > 0:
                        profit_growth_y2 = (ni_y1 / ni_y2) - 1
                    if pd.notnull(ni_y2) and pd.notnull(ni_y3) and ni_y3 > 0:
                        profit_growth_y3 = (ni_y2 / ni_y3) - 1
                else:
                    print(f"\n警告: 未能在 {ticker} 的财务数据中找到净利润项。可用项: {financials.index.tolist()}")

        except Exception as fin_e:
            print(f"\n获取或计算 {ticker} 详细财务数据时出错: {fin_e}")
            buyback_amount = 0 # 出错时视为0
            # 利润增长率也设为None
            profit_growth_y1 = None
            profit_growth_y2 = None
            profit_growth_y3 = None

        # 计算真实股息和真实股息率
        real_dividend = None
        real_dividend_yield = None
        if total_dividend_paid is not None and buyback_amount is not None:
            real_dividend = total_dividend_paid + buyback_amount
            if market_cap is not None and market_cap != 0:
                real_dividend_yield = real_dividend / market_cap

        return {
            'Ticker': ticker,
            'Name': info.get('shortName', ticker),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Gross Margin': gross_margin,
            'PE Ratio': pe_ratio,
            'ROE': roe,
            'Equity Multiplier': equity_multiplier,
            'Dividend Yield': dividend_yield, # 添加普通股息率 (已修正)
            'Real Dividend Yield': real_dividend_yield, # 添加真实股息率
            'Profit Growth Y1': profit_growth_y1, # 最近一年增长率
            'Profit Growth Y2': profit_growth_y2, # 前一年增长率
            'Profit Growth Y3': profit_growth_y3,  # 再前一年增长率
            'Short Term Debt to Cash Ratio': short_term_debt_cash_ratio, # 短期负债/现金
            'Interest Bearing Debt Ratio': debt_ratio # 添加有息负债率
        }
    except Exception as e:
        print(f"\n获取 {ticker} 的财务指标时出错: {e}")
        return {
            'Ticker': ticker,
            'Name': ticker,
            'Sector': 'N/A',
            'Industry': 'N/A',
            'Gross Margin': None,
            'PE Ratio': None,
            'ROE': None,
            'Equity Multiplier': None,
            'Dividend Yield': None, # 错误时也返回None
            'Real Dividend Yield': None, # 错误时也返回None
            'Profit Growth Y1': None,
            'Profit Growth Y2': None,
            'Profit Growth Y3': None,
            'Short Term Debt to Cash Ratio': None, # 错误时也返回None
            'Interest Bearing Debt Ratio': None # 错误时也返回None
        }

def main():
    print("欢迎使用财务数据分析脚本！")
    print("请选择要分析的股票组：")
    print("1. 标普500成分股 (默认)")
    print("2. 支付公司 (AXP, MA, V, DFS)")
    print("3. 饮料公司 (KO, PEP)")
    
    choice = input("请输入选项编号 (1-3，默认为1): ").strip()
    
    selected_group_name = "SP500"
    if choice == '2':
        tickers = ['AXP', 'MA', 'V', 'DFS']
        selected_group_name = "Payment_Companies"
        print(f"已选择分析支付公司: {tickers}")
    elif choice == '3':
        tickers = ['KO', 'PEP']
        selected_group_name = "Beverage_Companies"
        print(f"已选择分析饮料公司: {tickers}")
    else:
        # 默认或无效输入，选择标普500
        if choice != '1' and choice != '':
            print("无效输入，将默认分析标普500成分股。")
        tickers = get_sp500_tickers()
        print(f"开始获取标普500成分股财务数据...成功获取 {len(tickers)} 个成分股")

    if not tickers:
        print("未能获取到股票列表，程序退出。")
        return
    
    # 存储所有公司的财务指标
    all_metrics = []
    
    # 设置计数器和总数，用于显示进度
    total = len(tickers)
    count = 0
    
    # 遍历每个股票代码获取财务指标
    for ticker in tickers:
        count += 1
        print_progress(count, total, ticker, prefix="处理进度", suffix="")
        
        # 获取财务指标
        metrics = get_financial_metrics(ticker)
        all_metrics.append(metrics)
        
        # 每处理10个股票暂停一下，避免API限制
        if count % 10 == 0 and count < total:
            time.sleep(2)
    
    # 将结果转换为DataFrame
    df = pd.DataFrame(all_metrics)
    
    # 创建原始数据的副本，用于条件格式化
    df_original = df.copy()
    
    # 打印DataFrame的实际列名，用于调试
    print("\nDataFrame的实际列名:")
    print(df.columns.tolist())
    print("\nDataFrame_original的实际列名:")
    print(df_original.columns.tolist())
    
    # 格式化百分比列
    for col in ['Gross Margin', 'ROE', 'Dividend Yield', 'Real Dividend Yield', 'Profit Growth Y1', 'Profit Growth Y2', 'Profit Growth Y3', 'Interest Bearing Debt Ratio']:
        df[col] = df[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) and isinstance(x, (int, float)) else "N/A")
    
    # 格式化PE Ratio, Equity Multiplier 和 Short Term Debt to Cash Ratio
    for col in ['PE Ratio', 'Equity Multiplier', 'Short Term Debt to Cash Ratio']:
        df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else "N/A")

    # 创建输出目录（如果不存在）
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{selected_group_name}_Financial_Metrics_{timestamp}.xlsx")
    
    # 导出到Excel，但不立即保存，而是创建一个ExcelWriter对象
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='SP500')
        
        # 获取工作簿和工作表对象
        workbook = writer.book
        worksheet = writer.sheets['SP500']
        
        # 导入openpyxl的样式模块
        from openpyxl.styles import PatternFill

        # 定义填充颜色
        light_green_fill = PatternFill(start_color='FF90EE90', end_color='FF90EE90', fill_type='solid') # 浅绿色
        light_yellow_fill = PatternFill(start_color='FFFFFFE0', end_color='FFFFFFE0', fill_type='solid') # 浅黄色
        light_blue_fill = PatternFill(start_color='ADD8E6', end_color='ADD8E6', fill_type='solid') # 浅蓝色
        light_red_fill = PatternFill(start_color='FFFFC0CB', end_color='FFFFC0CB', fill_type='solid') # 浅红色 (淡粉色)
        light_gray_fill = PatternFill(start_color='FFE0E0E0', end_color='FFE0E0E0', fill_type='solid') # 浅灰色，用于隔行

        # 获取列索引
        ticker_col_idx = df.columns.get_loc('Ticker') + 1 # Excel列从1开始
        gm_col_idx = df.columns.get_loc('Gross Margin') + 1
        pe_col_idx = df.columns.get_loc('PE Ratio') + 1
        roe_col_idx = df.columns.get_loc('ROE') + 1
        em_col_idx = df.columns.get_loc('Equity Multiplier') + 1 # 获取权益乘数列索引
        real_col_idx = df.columns.get_loc('Real Dividend Yield') + 1 # 获取真实股息率列索引
        short_term_debt_cash_ratio_col_idx = df.columns.get_loc('Short Term Debt to Cash Ratio') + 1 # 获取短期负债与现金比率列索引

        # 遍历数据行，应用条件格式
        for row_idx, row in enumerate(df_original.iterrows(), start=2):  # Excel行从2开始（跳过标题行）
            # row是一个元组，包含索引和Series，我们需要的是Series部分
            _, data = row

            # --- 添加隔行换色 --- 
            # 默认白色，偶数行（Excel行号）使用浅灰色
            row_fill = None
            if row_idx % 2 == 0:
                row_fill = light_gray_fill
            
            # 应用基础行背景色到该行的所有单元格
            if row_fill:
                for col_idx in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    cell.fill = row_fill
            # --- 隔行换色结束 ---

            # 获取原始数值用于判断
            gm = data['Gross Margin']
            pe = data['PE Ratio']
            roe = data['ROE']
            em = data['Equity Multiplier'] # 获取原始权益乘数值
            real_val = data['Real Dividend Yield'] # 获取原始真实股息率数值
            short_term_debt_cash_ratio_val = data['Short Term Debt to Cash Ratio'] # 获取原始短期负债与现金比率数值

            # 获取 Ticker 单元格
            ticker_cell = worksheet.cell(row=row_idx, column=ticker_col_idx)

            # 检查所有指标是否有效
            gm_valid = pd.notnull(gm) and isinstance(gm, (int, float))
            pe_valid = pd.notnull(pe) and isinstance(pe, (int, float))
            roe_valid = pd.notnull(roe) and isinstance(roe, (int, float))
            em_valid = pd.notnull(em) and isinstance(em, (int, float)) # 检查权益乘数有效性
            real_valid = pd.notnull(real_val) and isinstance(real_val, (int, float)) # 检查真实股息率有效性
            short_term_debt_cash_ratio_valid = pd.notnull(short_term_debt_cash_ratio_val) and isinstance(short_term_debt_cash_ratio_val, (int, float)) # 检查短期负债与现金比率有效性

            # 应用条件格式到 Ticker 列 (优先级：绿 > 蓝 > 黄 > 红)
            if gm_valid and pe_valid and roe_valid and gm > 0.6 and pe < 50 and roe > 0.2:
                ticker_cell.fill = light_green_fill # 最佳：浅绿
            elif gm_valid and pe_valid and roe_valid and gm > 0.4 and gm <= 0.6 and pe < 50 and roe > 0.2:
                ticker_cell.fill = light_blue_fill # 次佳：浅蓝
            elif gm_valid and roe_valid and gm > 0.6 and roe > 0.2 and (not pe_valid or pe >= 50):
                ticker_cell.fill = light_yellow_fill # 警告：浅黄 (PE不满足)
            else:
                ticker_cell.fill = light_red_fill # 其他情况：浅红

            # 应用条件格式到单个指标单元格
            # 检查毛利率是否低于60%
            if gm_valid and gm < 0.6:
                cell = worksheet.cell(row=row_idx, column=gm_col_idx)
                cell.fill = light_red_fill # 使用浅红色

            # 检查PE是否大于50
            if pe_valid and pe > 50:
                cell = worksheet.cell(row=row_idx, column=pe_col_idx)
                cell.fill = light_red_fill # 使用浅红色

            # 检查ROE是否小于20%
            if roe_valid and roe < 0.2:
                cell = worksheet.cell(row=row_idx, column=roe_col_idx)
                cell.fill = light_red_fill # 使用浅红色

            # 检查真实股息率是否大于10%
            if real_valid and real_val > 0.10:
                cell = worksheet.cell(row=row_idx, column=real_col_idx)
                cell.fill = light_green_fill # 使用浅绿色

            # 检查短期负债与现金比率是否大于1
            if short_term_debt_cash_ratio_valid and short_term_debt_cash_ratio_val > 1:
                cell = worksheet.cell(row=row_idx, column=short_term_debt_cash_ratio_col_idx)
                cell.fill = light_red_fill # 使用浅红色
    
    print(f"\n处理完成! 共处理了 {len(all_metrics)} 个公司的财务数据")
    print(f"结果已保存到: {output_file}")
    
    # 显示一些统计信息
    valid_gm = df[df['Gross Margin'] != 'N/A']
    valid_pe = df[df['PE Ratio'] != 'N/A']
    valid_roe = df[df['ROE'] != 'N/A']
    valid_em = df[df['Equity Multiplier'] != 'N/A'] # 检查有效的权益乘数
    valid_dy = df[df['Dividend Yield'] != 'N/A'] # 检查有效的股息率
    valid_real = df[df['Real Dividend Yield'] != 'N/A'] # 检查有效的真实股息率
    valid_pg1 = df[df['Profit Growth Y1'] != 'N/A'] # 检查有效的利润增长率Y1
    valid_pg2 = df[df['Profit Growth Y2'] != 'N/A'] # 检查有效的利润增长率Y2
    valid_pg3 = df[df['Profit Growth Y3'] != 'N/A'] # 检查有效的利润增长率Y3
    valid_short_term_debt_cash_ratio = df[df['Short Term Debt to Cash Ratio'] != 'N/A'] # 检查有效的短期负债与现金比率
    valid_debt_ratio = df[df['Interest Bearing Debt Ratio'] != 'N/A'] # 检查有效的有息负债率

    print(f"\n数据统计:")
    print(f"- 成功获取毛利率数据的公司数: {len(valid_gm)} / {len(df)}")
    print(f"- 成功获取市盈率数据的公司数: {len(valid_pe)} / {len(df)}")
    print(f"- 成功获取ROE数据的公司数: {len(valid_roe)} / {len(df)}")
    print(f"- 成功获取权益乘数数据的公司数: {len(valid_em)} / {len(df)}") # 添加权益乘数统计
    print(f"- 成功获取股息率数据的公司数: {len(valid_dy)} / {len(df)}") # 添加股息率统计
    print(f"- 成功获取真实股息率数据的公司数: {len(valid_real)} / {len(df)}") # 添加真实股息率统计
    print(f"- 成功获取最近1年利润增长率数据的公司数: {len(valid_pg1)} / {len(df)}") # 添加利润增长率统计
    print(f"- 成功获取最近2年利润增长率数据的公司数: {len(valid_pg2)} / {len(df)}") # 添加利润增长率统计
    print(f"- 成功获取最近3年利润增长率数据的公司数: {len(valid_pg3)} / {len(df)}") # 添加利润增长率统计
    print(f"- 成功获取短期负债与现金比率数据的公司数: {len(valid_short_term_debt_cash_ratio)} / {len(df)}") # 添加短期负债与现金比率统计
        # 播放开始提示音 (Windows系统)
    try:
        print("尝试播放启动提示音...") # 添加调用前打印
        winsound.Beep(800, 1000) # 播放一个简短的启动音
        print(f"winsound.Beep 调用完成，未引发异常。") # 添加调用后打印
    except RuntimeError as re: # 捕获特定的运行时错误
        print(f"播放启动提示音时发生运行时错误: {re}")
    except Exception as e: # 捕获其他一般性错误
        print(f"播放启动提示音时发生其他错误: {e}")
        

if __name__ == "__main__":
    main()