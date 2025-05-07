update:
	poetry update
500:
	poetry run python finance/500.py
clear:
	poetry env remove -all
pe:
	poetry run python finance/pe_trend.py
