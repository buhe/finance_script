update:
	poetry update
500:
	poetry run python finance/500.py
clear:
	poetry env remove -all
gfw_windows:
	$env:http_proxy = "127.0.0.1:7890"
	$env:https_proxy = "127.0.0.1:7890"