NAME := scroller
INSTALL_STAMP := .install.stamp

.DEFAULT_GOAL := help

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "\033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: install
install: $(INSTALL_STAMP) ## Installs project dependencies via poetry
$(INSTALL_STAMP): pyproject.toml poetry.lock
	@if [ -z poetry ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	poetry install
	touch $(INSTALL_STAMP)

.PHONY: generate
generate: $(INSTALL_STAMP) ## Generates qrc file from .qml object files
	@if [ -z poetry ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	@echo "Generating QRC"
	@poetry run pyside6-rcc scroller/qml.qrc -o scroller/qml_rc.py

.PHONY: build
build: $(INSTALL_STAMP) generate ## Builds application package
	@poetry run python -m PyInstaller bin/scroller.spec --noconfirm
	@cat bin/unnecessary_build_files.txt | xargs rm -rf

.PHONY: run
run: $(INSTALL_STAMP) generate ## Runs the application
	@if [ -z poetry ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	poetry run $(NAME)

.PHONY: clean
clean: ## Cleanup all artifacts
	@find . -type d -name "__pycache__" | xargs rm -rf {};
	@rm -rf $(INSTALL_STAMP) .coverage .mypy_cache

.PHONY: lint
lint: $(INSTALL_STAMP) ## Lint all python files
	poetry run isort --profile=black --lines-after-imports=2 --check-only ./tests/ $(NAME)
	poetry run black --check ./tests/ $(NAME) --diff
	poetry run flake8 --ignore=W503,E501 ./tests/ $(NAME)
	poetry run mypy ./tests/ $(NAME) --ignore-missing-imports
	poetry run bandit -r $(NAME) -s B608

.PHONY: format
format: $(INSTALL_STAMP) ## Format all python files
	poetry run isort --profile=black --lines-after-imports=2 ./tests/ $(NAME)
	poetry run black ./tests/ $(NAME)

.PHONY: test
test: $(INSTALL_STAMP) ## Run tests
	poetry run pytest ./tests/ --cov-report term-missing --cov $(NAME)