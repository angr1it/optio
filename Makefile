SHELL := /bin/bash
PYTHON ?= python3
PNPM ?= pnpm

.PHONY: build test lint typecheck check smoke \
	project-format project-test validator-test governance-check \
	hooks-pre-commit hooks-pre-push \
	docs-lint language-lint backlog-lint features-lint iterations-lint \
	new-backlog new-feature new-iteration

build:
	@$(PNPM) build

validator-test:
	@$(PYTHON) -m unittest discover -s tools/scripts -p 'test_*.py'

project-format:
	@$(PNPM) format:check

project-test:
	@$(PNPM) turbo test

test: validator-test project-test

governance-check: docs-lint language-lint backlog-lint features-lint iterations-lint validator-test

lint: project-format governance-check

typecheck:
	@$(PNPM) turbo typecheck

hooks-pre-commit: project-format governance-check typecheck

hooks-pre-push: check

docs-lint:
	@$(PYTHON) tools/scripts/docs_lint.py

language-lint:
	@$(PYTHON) tools/scripts/language_lint.py

backlog-lint:
	@$(PYTHON) tools/scripts/validate_backlog.py

features-lint:
	@$(PYTHON) tools/scripts/validate_features.py

iterations-lint:
	@$(PYTHON) tools/scripts/validate_iterations.py

check: lint typecheck test

smoke: check

new-backlog:
	@$(PYTHON) tools/scripts/scaffold_docs.py backlog \
		--id "$(ID)" \
		--title "$(TITLE)" \
		--owner "$(if $(OWNER),$(OWNER),platform)" \
		--priority "$(if $(PRIORITY),$(PRIORITY),Medium)" \
		--state "$(if $(STATE),$(STATE),Proposed)" \
		--target-iteration "$(if $(TARGET),$(TARGET),TBD)"

new-feature:
	@$(PYTHON) tools/scripts/scaffold_docs.py feature \
		--name "$(NAME)" \
		--backlog-id "$(BACKLOG)" \
		--owner "$(if $(OWNER),$(OWNER),platform)" \
		--iteration-id "$(if $(ITERATION),$(ITERATION),ITR-###)" \
		$(if $(TITLE),--title "$(TITLE)",) \
		$(if $(FORCE),--force,)

new-iteration:
	@$(PYTHON) tools/scripts/scaffold_docs.py iteration \
		--id "$(ID)" \
		$(foreach bid,$(BACKLOG_IDS),--backlog-id "$(bid)") \
		--owner "$(if $(OWNER),$(OWNER),platform)" \
		$(if $(TITLE),--title "$(TITLE)",) \
		$(if $(FORCE),--force,)
