PROJECT ?= movies_admin
REQUIREMENTS ?= requirements-dev.txt
VIRTUAL_ENV ?= .venv
PYTHON ?= $(VIRTUAL_ENV)/bin/python

PYTHON_VERSION ?= 3.11.0

RUN := . $(VIRTUAL_ENV)/bin/activate ;

# Private commands
include .etc/Makefile

# Piptools commands
PIP_COMPILE_PROD := $(PIP_COMPILE) .meta/requirements.in -o .meta/packages
PIP_COMPILE_DEV := $(PIP_COMPILE) .meta/requirements.in .meta/requirements-dev.in -o .meta/packages.dev

# Setup environments
init: _create_venv _install_piptools

install:
	$(PIP_SYNC) .meta/packages.dev

install_no_dev:
	$(PIP_SYNC) .meta/packages

venv: init install

# Manage dependencies
compile:
	$(PIP_COMPILE_PROD)
	$(PIP_COMPILE_DEV)

lock: compile

update:
	$(PIP_COMPILE_PROD) -U
	$(PIP_COMPILE_DEV) -U

# Clean up
clean_pyc:
	find . -name \*.pyc -delete

clean: clean_pyc
	rm -rf $(VIRTUAL_ENV) .cache .reports

# Test and lint
coverage:
	$(RUN) pytest . -vv --cov

ruff:
	$(RUN) ruff check .

lint: ruff

test: venv lint coverage
