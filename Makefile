PYTHON_VERSION = python3.12

setup:
	poetry env use $(PYTHON_VERSION)
	poetry install

clean:
	poetry env remove $(PYTHON_VERSION)

check:
	check-lint check-typing check-format

check-format:
	@OUTPUT=$(poetry run ruff format --check . 2>&1); \
	if [ $$? -eq 0 ]; then \
		echo "Code is formatted correctly" \
	else \
		echo "Code formatting errors:" \
		echo "$$OUTPUT" \
		exit 1 \
	fi

check-lint:
    @OUTPUT=$(poetry run ruff check . 2>&1); \
    if [ $$? -eq 0 ]; then \
        echo "Code is lint-free" \
    else \
        echo "Linting errors:" \
        echo "$$OUTPUT" \
        exit 1 \
    fi

check-typing:
    @OUTPUT=$(poetry run mypy ./app 2>&1); \
    if [ $$? -eq 0 ]; then \
        echo "Type checks passed" \
    else \
        echo "Type checking errors:" \
        echo "$$OUTPUT" \
        exit 1 \
    fi

test:
	poetry run pytest

update:
	git pull
	poetry update

format:
	poetry run ruff format .

checkfix:
	poetry run ruff check --fix .

rebase:
	git pull --rebase origin dev

push: 
	check test
	git push origin