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
        # 毛利率 = (总收入 - 销售成本) / 总收入
        gross_margin = info.get('grossMargins', None)
        
        # 获取市盈率 (PE Ratio)
        pe_ratio = info.get('trailingPE', None)
        
        # 计算净资产收益率 (ROE)
        # ROE = 净利润 / 股东权益
        roe = info.get('returnOnEquity', None)

        # 获取资产负债表数据以计算权益乘数
        equity_multiplier = None
        try:
            balance_sheet = stock.balance_sheet
            if not balance_sheet.empty:
                latest_bs = balance_sheet.iloc[:, 0] # 获取最新一期数据
                total_assets = latest_bs.get('Total Assets', None)
                # 尝试不同的股东权益名称
                total_equity = latest_bs.get('Total Stockholder Equity', None)
                if total_equity is None:
                    total_equity = latest_bs.get('Stockholders Equity', None)
                if total_equity is None:
                    total_equity = latest_bs.get('Total Equity Gross Minority Interest', None)

                if total_assets is not None and total_equity is not None and total_equity != 0:
                    equity_multiplier = total_assets / total_equity
        except Exception as bs_e:
            # 打印获取资产负债表或计算时的错误，但不中断流程
            print(f"\n获取或计算 {ticker} 权益乘数时出错: {bs_e}")

        return {
            'Ticker': ticker,
            'Name': info.get('shortName', ticker),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Gross Margin': gross_margin,
            'PE Ratio': pe_ratio,
            'ROE': roe,
            'Equity Multiplier': equity_multiplier # 添加权益乘数
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
            'Equity Multiplier': None # 错误时也返回None
        }

def main():
    print("开始获取标普500成分股财务数据...")
    
    # 获取标普500成分股列表
    tickers = get_sp500_tickers()
    print(f"成功获取 {len(tickers)} 个标普500成分股")
    
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
    for col in ['Gross Margin', 'ROE']:
        df[col] = df[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) and isinstance(x, (int, float)) else "N/A")
    
    # 格式化PE Ratio 和 Equity Multiplier
    for col in ['PE Ratio', 'Equity Multiplier']:
        df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else "N/A")
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"SP500_Financial_Metrics_{timestamp}.xlsx")
    
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

        # 获取列索引
        ticker_col_idx = df.columns.get_loc('Ticker') + 1 # Excel列从1开始
        gm_col_idx = df.columns.get_loc('Gross Margin') + 1
        pe_col_idx = df.columns.get_loc('PE Ratio') + 1
        roe_col_idx = df.columns.get_loc('ROE') + 1
        em_col_idx = df.columns.get_loc('Equity Multiplier') + 1 # 获取权益乘数列索引

        # 遍历数据行，应用条件格式
        for row_idx, row in enumerate(df_original.iterrows(), start=2):  # Excel行从2开始（跳过标题行）
            # row是一个元组，包含索引和Series，我们需要的是Series部分
            _, data = row

            # 获取原始数值用于判断
            gm = data['Gross Margin']
            pe = data['PE Ratio']
            roe = data['ROE']
            em = data['Equity Multiplier'] # 获取原始权益乘数值

            # 获取 Ticker 单元格
            ticker_cell = worksheet.cell(row=row_idx, column=ticker_col_idx)

            # 检查所有指标是否有效
            gm_valid = pd.notnull(gm) and isinstance(gm, (int, float))
            pe_valid = pd.notnull(pe) and isinstance(pe, (int, float))
            roe_valid = pd.notnull(roe) and isinstance(roe, (int, float))
            em_valid = pd.notnull(em) and isinstance(em, (int, float)) # 检查权益乘数有效性

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
    
    print(f"\n处理完成! 共处理了 {len(all_metrics)} 个公司的财务数据")
    print(f"结果已保存到: {output_file}")
    
    # 显示一些统计信息
    valid_gm = df[df['Gross Margin'] != 'N/A']
    valid_pe = df[df['PE Ratio'] != 'N/A']
    valid_roe = df[df['ROE'] != 'N/A']
    valid_em = df[df['Equity Multiplier'] != 'N/A'] # 检查有效的权益乘数
    
    print(f"\n数据统计:")
    print(f"- 成功获取毛利率数据的公司数: {len(valid_gm)} / {len(df)}")
    print(f"- 成功获取市盈率数据的公司数: {len(valid_pe)} / {len(df)}")
    print(f"- 成功获取ROE数据的公司数: {len(valid_roe)} / {len(df)}")
    print(f"- 成功获取权益乘数数据的公司数: {len(valid_em)} / {len(df)}") # 添加权益乘数统计
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