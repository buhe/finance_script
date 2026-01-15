# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common Commands

### Running Analysis Scripts
```bash
# Run S&P 500 financial analysis (interactive)
python3 500.py

# Run asset allocation analysis
python3 assetAllocation.py

# Run P/E ratio trend analysis (interactive - prompts for ticker)
python3 pe_trend.py

# Run correlation analysis
python3 pearsonr.py   # KWEB vs S&P 500
python3 pearsonr2.py  # AAPL vs S&P 500  
python3 pearsonr3.py  # Multiple asset correlations

# Simple yfinance debug test
python3 yahoo.py

# Basic dividend data fetch
python3 div.py
```

### Installation & Dependencies
```bash
# Install required packages
pip3 install yfinance pandas matplotlib scipy openpyxl numpy
```

### Testing Individual Scripts
```bash
# Test basic yfinance functionality
python3 -c "import yfinance as yf; print(yf.download('AAPL', period='1d'))"

# Test matplotlib display
python3 -c "import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.show()"
```

## Code Architecture & Structure

### Core Modules

**500.py** - The main financial analysis engine
- Fetches S&P 500 constituent data from Wikipedia
- Downloads comprehensive financial metrics for stocks using yfinance
- Calculates advanced metrics: gross margins, P/E ratios, ROE, equity multipliers, real dividend yields, profit growth rates
- Supports analysis of multiple stock groups: S&P 500, payment companies, beverage companies, luxury goods, A-shares, HK shares
- Exports results to Excel with conditional formatting (color-coded based on financial health)
- Includes progress tracking and Windows audio notifications

**assetAllocation.py** - Portfolio analysis and asset allocation modeling
- Implements custom asset allocation strategy with multiple asset classes
- Calculates annualized returns and volatility for portfolio vs benchmarks
- Includes complex custom functions: `popAndPad()` for time-series manipulation, `vsAndAnnualized()` for return calculations
- Visualizes portfolio performance against S&P 500, CSI 300, gold, bonds, and other indexes
- Handles different asset types: equities, bonds, commodities, real estate, cash deposits

**pe_trend.py** - Historical P/E ratio analysis
- Interactive script that prompts for ticker symbols
- Downloads historical financial statements and stock prices
- Calculates annual P/E ratios based on fiscal year-end data
- Handles EPS data extraction from yfinance with multiple fallback column names
- Creates trend visualization with current P/E overlay
- Includes comprehensive error handling for missing or invalid data

**pearsonr*.py series** - Correlation analysis tools
- Calculate Pearson correlation coefficients between different assets
- Compare Chinese assets (KWEB, ASHR) with US markets (S&P 500)
- Analyze relationships between stocks, bonds (TLT), and commodities (GLD)
- Use 10-year lookback periods with 100-day lag from current date

### Data Flow Pattern

1. **Data Acquisition**: All scripts use yfinance as the primary data source
2. **Processing**: Raw financial data is cleaned, calculated, and transformed
3. **Analysis**: Scripts apply financial formulas and statistical methods
4. **Visualization**: matplotlib generates charts and graphs
5. **Export**: Results saved to Excel files in `/output/` directory with timestamps

### Key Dependencies & Their Usage

- **yfinance**: Primary financial data API (stocks, ETFs, indices)
- **pandas**: Data manipulation, DataFrame operations, Excel I/O
- **matplotlib**: All chart generation and data visualization
- **scipy.stats**: Pearson correlation calculations
- **openpyxl**: Excel file creation with advanced formatting
- **numpy**: Mathematical operations, especially in asset allocation
- **winsound**: Audio notifications (Windows-specific, may need alternatives on macOS/Linux)

### Output Structure

All analysis results are saved to `/output/` directory with naming convention:
`{Group_Name}_Financial_Metrics_{YYYYMMDD_HHMMSS}.xlsx`

Excel files include:
- Conditional formatting (green=excellent, blue=good, yellow=warning, red=poor)
- Color-coded metrics based on financial health thresholds
- Alternating row colors for readability

### Financial Metrics & Thresholds

The codebase uses specific financial health criteria:
- **Excellent (Green)**: Gross Margin >60%, P/E <50, ROE >20%
- **Good (Blue)**: Gross Margin 40-60%, P/E <50, ROE >20%  
- **Warning (Yellow)**: High gross margin & ROE but P/E ≥50
- **Poor (Red)**: Below thresholds or missing data

**Real Dividend Yield**: Combines traditional dividends + share buybacks for more accurate shareholder returns

### Asset Allocation Strategy

The `assetAllocation.py` implements a specific portfolio allocation:
- 22% VOO (S&P 500)
- Chinese equities (Moutai, CMB via SS/SZ tickers)
- Commodities (GLD)
- Bonds (TLT, Chinese 10Y)
- Individual stocks (AAPL, TCEHY, API)
- Cash/CDs (23% allocation)
- Real estate (17% allocation)

### Language & Localization

- Code comments mix English and Chinese
- Some user-facing messages in Chinese (especially in 500.py and pe_trend.py)
- Error messages and debug output primarily in Chinese
- Excel output uses English column headers

### Platform Considerations

- **Windows-specific**: `winsound` module for audio notifications
- **Cross-platform**: All other dependencies work on macOS/Linux
- Uses timezone-aware datetime handling for international markets
- Supports multiple stock exchanges (.SS, .SZ, .HK, .PA, .SW suffixes)
