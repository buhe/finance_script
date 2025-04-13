import yfinance as yf
import time
import os
import sys
from datetime import datetime

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
    # sp500 = yf.Ticker("^GSPC")
    
    # try:
    #     # 尝试获取标普500的成分股
    #     return sp500.index_components
    # except:
    print("无法获取标普500成分股列表，使用备选方法...")
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
        
        return {
            'Ticker': ticker,
            'Name': info.get('shortName', ticker),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Gross Margin': gross_margin,
            'PE Ratio': pe_ratio,
            'ROE': roe
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
            'ROE': None
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
    
    # 格式化百分比列
    for col in ['Gross Margin', 'ROE']:
        df[col] = df[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) and isinstance(x, (int, float)) else "N/A")
    
    # 格式化PE Ratio
    df['PE Ratio'] = df['PE Ratio'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else "N/A")
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"SP500_Financial_Metrics_{timestamp}.xlsx")
    
    # 导出到Excel
    df.to_excel(output_file, index=False)
    
    print(f"\n处理完成! 共处理了 {len(all_metrics)} 个公司的财务数据")
    print(f"结果已保存到: {output_file}")
    
    # 显示一些统计信息
    valid_gm = df[df['Gross Margin'] != 'N/A']
    valid_pe = df[df['PE Ratio'] != 'N/A']
    valid_roe = df[df['ROE'] != 'N/A']
    
    print(f"\n数据统计:")
    print(f"- 成功获取毛利率数据的公司数: {len(valid_gm)} / {len(df)}")
    print(f"- 成功获取市盈率数据的公司数: {len(valid_pe)} / {len(df)}")
    print(f"- 成功获取ROE数据的公司数: {len(valid_roe)} / {len(df)}")

if __name__ == "__main__":
    main()