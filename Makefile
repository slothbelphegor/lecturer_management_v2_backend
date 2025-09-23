VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
.PHONY: run clean venv

run: install
	$(PYTHON) manage.py runserver

migrate: 
	$(PYTHON) manage.py makemigrations
	$(PYTHON) manage.py migrate

clean:
	rm -rf __pycache__
	rm -rf $(VENV)

activate: install
	. $(VENV)/bin/activate

install: requirements.txt 
	python3 -m venv $(VENV)
	$(PYTHON) -m ensurepip --upgrade
	$(PIP) install -r requirements.txt
	
reinstall: 
	python3 -m venv $(VENV)
	$(PIP) install requirements/* --force-reinstall

flake8: 
	flake8 --exclude=__pycache__,venv,*.txt