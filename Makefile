.DEFAULT_GOAL := help

BASE_REF ?= main

.PHONY: help install install-dev install-llm install-all lint test test-unit test-integration check jobs-list jobs-cron doc-gate

help: ## List available targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "%-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install base package
	pip install -e .

install-llm: ## Install LLM extras
	pip install -e ".[llm]"

install-dev: ## Install development environment
	pip install -e ".[llm,web,dev]"

install-all: ## Install all optional extras
	pip install -e ".[llm,pdf,ocr,web,dev]"

lint: ## Run Ruff lint checks
	ruff check kb tests

test: ## Run full pytest suite
	python -m pytest

test-unit: ## Run unit tests only
	python -m pytest tests/unit/

test-integration: ## Run integration tests only
	python -m pytest tests/integration/

check: ## Run lint and full test suite
	$(MAKE) lint
	$(MAKE) test

jobs-list: ## List canonical kb jobs
	kb jobs list

jobs-cron: ## Print suggested kb cron block
	kb jobs cron

doc-gate: ## Run documentation conformity gate
	kb jobs doc-gate --base-ref $(BASE_REF)
