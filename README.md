# Finance

## Script

To install dependencies using Poetry:

```
poetry install
```

To run a Python script (e.g., `xx.py`) using Poetry:

```
poetry run python3 xx.py
```

Specific scripts:

- To run the Pearson correlation script:  
  ```
  poetry run python3 finance/pearsonr.py
  ```

- To run the asset allocation script:  
  ```
  poetry run python3 finance/assetAllocation.py
  ```

- To run the S&P 500 related script:  
  ```
  poetry run python3 finance/500.py
  ```

## Summary

- The correlation coefficient between the Shanghai and Shenzhen 300 Index and the S&P 500 Index over the past 10 years is: **0.4266**

- The correlation coefficient between the Shanghai and Shenzhen 300 Index and the Gold Index over the past 10 years is: **0.0683**

- The correlation coefficient between TLT and the S&P 500 Index over the past 10 years is: **-0.2242**

- The correlation coefficient between the Gold Index and the S&P 500 Index over the past 10 years is: **0.0280**

- The script `500.py` is used to obtain the PE (Price-to-Earnings ratio), gross margin, and ROE (Return on Equity) of the S&P 500.