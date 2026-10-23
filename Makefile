PY ?= python

.PHONY: install data run clean all

install:
	$(PY) -m pip install -r requirements.txt

data:
	$(PY) scripts/download_data.py

run:
	streamlit run app.py

clean:
	rm -rf data/processed/* data/raw/*.csv

all: install data run
