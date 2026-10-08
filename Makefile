# kOMA desktop theme — developer tasks.  `make setup` once, then `make check` before committing
# (the pre-commit hook runs it for you).

export NPM_CONFIG_LOGLEVEL = warn
SHELL_SCRIPTS := install.sh uninstall.sh get-koma.sh scripts/*.sh setup/*.sh .githooks/pre-commit
PYTHON_SOURCES := $(shell git ls-files '*.py')

.PHONY: setup lint test check pins packages release clean

setup:  ## ShellCheck into node_modules, and enable the git hook
	npm install --silent --no-fund --no-audit
	git config core.hooksPath .githooks

lint:  ## static gates, and packages/ matching their sources
	python3 -m py_compile $(PYTHON_SOURCES)
	npx --no-install shellcheck $(SHELL_SCRIPTS)
	python3 scripts/build-packages.py --check
	python3 scripts/update-pins.py --check

test:  ## installer unit tests
	python3 -m unittest discover -s tests

check: lint test  ## what the pre-commit hook runs

pins:  ## pin the kOMA widgets to their latest GitHub releases
	python3 scripts/update-pins.py

packages:  ## rebuild the Global Theme and Colors packages from source
	python3 scripts/build-packages.py

release: check  ## dist/: installer bundle, get-koma.sh, SHA256SUMS
	scripts/release.sh

clean:
	rm -rf dist
