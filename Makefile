.PHONY: install validate pipeline dashboard test report
install:
	python -m pip install -r requirements.txt
validate:
	python -m src.cli validate
pipeline:
	python -m src.cli run-all
dashboard:
	streamlit run app.py
test:
	pytest -q
report:
	python -m src.cli report --period monthly
