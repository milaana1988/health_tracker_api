.PHONY: format check

format:
	black app

check:
	black --check app
