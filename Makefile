PY ?= python
RANKER ?= keyword
SPLIT ?= dev

export PYTHONPATH := src

.PHONY: install test prepare build-index verify serve eval boolean clean

install:
	$(PY) -m pip install -e ".[dev]"

test:
	$(PY) -m pytest -q

prepare:
	$(PY) -m rayu_rag prepare

build-index:
	$(PY) -m rayu_rag build-index

verify:
	$(PY) -m rayu_rag verify

serve:
	$(PY) -m rayu_rag serve

eval:
	$(PY) -m rayu_rag eval --ranker $(RANKER) --split $(SPLIT)

boolean:
	$(PY) -m rayu_rag boolean "$(EXPR)"

clean:
	rm -rf artifacts reports .pytest_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
