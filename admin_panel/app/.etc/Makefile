PIP_COMPILE := $(RUN) pip-compile --no-header -v --no-emit-trusted-host --no-emit-index-url --resolver=backtracking
PIP_SYNC := $(RUN) pip-sync

PIP_VERSION ?= 23.3.1

_check_python_version:
	@PYTHON_=$$($(RUN) python -V) && \
	if [ ! "$${PYTHON_}" = "Python ${PYTHON_VERSION}" ]; then \
  		echo "You must use Python ${PYTHON_VERSION}"; \
  		echo "You are using $${PYTHON_}"; \
  		make clean; \
  		exit 1; \
  fi

_install_piptools:
	$(RUN) pip install "pip==${PIP_VERSION}"
	$(RUN) pip install pip-tools==7.3.0

_create_venv:
	if [ ! -d "${VIRTUAL_ENV}" ]; then \
		python -m venv $(VIRTUAL_ENV) --prompt $(PROJECT); \
	fi
	make _check_python_version
