python = venv/bin/python
pip = venv/bin/pip
pytest = venv/bin/pytest

uninstall-unrequired-libraries:
	$(pip) freeze | grep -v -f requirements.txt - | grep -v '^#' | xargs $(pip) uninstall -y || echo "OK, you dont have any unrequired libraries"

install: uninstall-unrequired-libraries
	$(pip) install -r requirements.txt

install-venv:
	python -m virtualenv venv --python python3

update-requirements:
	$(pip) freeze > requirements.txt

test: clean
	mkdir -p logs
	$(pytest) -vvvv tests

coverage: clean
	mkdir -p logs
	$(pytest) --cov-config=./pyproject.toml --cov=app tests/ --cov-report term-missing

clean-logs:
	rm -f logs/*.log
	rm -f logs/*.log.jsonl

clean-test-reports:
	mkdir -p test_reports
	rm -f test_reports/*.xml

clean: clean-logs clean-test-reports
