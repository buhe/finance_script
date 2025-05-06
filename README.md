# Finance

This project uses Poetry for dependency management and running scripts.

## Installation

1.  **Install Poetry:**

    If you don't have Poetry installed, you can install it by following the official instructions at [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation).

2.  **Install Project Dependencies:**

    Navigate to the project root directory and run:
    ```
    poetry install
    ```
3. If you at China homeland, you need set proxy to break the gfw(e.g. as Prowershell):

    ```
    $env:http_proxy = "127.0.0.1:7890"
    $env:https_proxy = "127.0.0.1:7890"
    ```
## Scripts

To run a Python script (e.g., `xx.py`) using Poetry:

```
poetry run python3 xx.py
```

Specific scripts:

-   To run the S&P 500 related script:
    ```
    poetry run python3 finance/500.py
    ```

-   To fetch PE trends:
    ```
    poetry run python3 finance/pe_trend.py
    ```
