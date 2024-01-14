NAME := scroller
INSTALL_STAMP := .install.stamp

.DEFAULT_GOAL := help

.PHONY: help
help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make [target]\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "\033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: install
install: $(INSTALL_STAMP) ## Install project dependencies via poetry

# Target to create the install stamp file
$(INSTALL_STAMP): pyproject.toml poetry.lock
	@echo "Installing dependencies..."
	@poetry install
	@touch $(INSTALL_STAMP)

.PHONY: generate
generate: $(INSTALL_STAMP) ## Generate qrc file from .qml object files
	@echo "Generating QRC"
	@poetry run pyside6-rcc $(NAME)/qml.qrc -o $(NAME)/qml_rc.py

.PHONY: build
build: $(INSTALL_STAMP) generate ## Build application package
	@echo "Building application..."
	@poetry run python -m PyInstaller bin/$(NAME).spec --noconfirm
	@cat bin/unnecessary_build_files.txt | xargs rm -rf

.PHONY: run
run: $(INSTALL_STAMP) generate ## Run the application
	@poetry run $(NAME)

.PHONY: clean
clean: ## Clean up all artifacts
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" | xargs rm -rf
	@rm -rf $(INSTALL_STAMP) .coverage .mypy_cache

.PHONY: lint
lint: $(INSTALL_STAMP) ## Lint all python files
	@echo "Running linters..."
	@poetry run isort --profile=black --lines-after-imports=2 --check-only ./tests/ $(NAME)
	@poetry run black --check ./tests/ $(NAME) --diff
	@poetry run flake8 --ignore=W503,E501 ./tests/ $(NAME)
	@poetry run mypy ./tests/ $(NAME) --ignore-missing-imports
	@poetry run bandit -r $(NAME) -s B608

.PHONY: format
format: $(INSTALL_STAMP) ## Format all python files
	@echo "Formatting source code..."
	@poetry run isort --profile=black --lines-after-imports=2 ./tests/ $(NAME)
	@poetry run black ./tests/ $(NAME)

.PHONY: test
test: $(INSTALL_STAMP) ## Run tests
	@echo "Running tests..."
	@poetry run pytest ./tests/ --cov-report term-missing --cov-fail-under 55 --cov $(NAME)
