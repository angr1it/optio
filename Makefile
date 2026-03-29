SHELL := /bin/bash
PYTHON ?= python3
PNPM ?= pnpm

.PHONY: build test lint typecheck check smoke \
	project-format project-test validator-test governance-check \
	hooks-pre-commit hooks-pre-push \
	docs-lint language-lint specs-lint change-scope-lint \
	new-spec

build:
	@$(PNPM) build

validator-test:
	@$(PYTHON) -m unittest discover -s tools/scripts -p 'test_*.py'

project-format:
	@$(PNPM) format:check

project-test:
	@$(PNPM) turbo test

test: validator-test project-test

governance-check: docs-lint language-lint specs-lint change-scope-lint validator-test

lint: project-format governance-check

typecheck:
	@$(PNPM) turbo typecheck

hooks-pre-commit: project-format governance-check typecheck

hooks-pre-push: check

docs-lint:
	@$(PYTHON) tools/scripts/docs_lint.py

language-lint:
	@$(PYTHON) tools/scripts/language_lint.py

specs-lint:
	@$(PYTHON) tools/scripts/validate_specs.py

change-scope-lint:
	@OPTIO_SPEC_REF="$(SPEC_REF)" $(PYTHON) tools/scripts/validate_change_scope.py

check: lint typecheck test

smoke: check

new-spec:
	@$(PYTHON) tools/scripts/scaffold_docs.py spec \
		--name "$(NAME)" \
		--owner "$(if $(OWNER),$(OWNER),platform)" \
		--issue "$(if $(ISSUE),$(ISSUE),N/A (local pre-deploy planning))" \
		--stage "$(if $(STAGE),$(STAGE),Local pre-deploy)" \
		$(if $(TITLE),--title "$(TITLE)",) \
		$(if $(FORCE),--force,)
