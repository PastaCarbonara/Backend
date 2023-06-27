# MealMatch backend repository

Hosted backend: https://munchie.azurewebsites.net/api/latest/docs

## To run the project

`python -m virualenv venv`

`.\venv\Scripts\activate`

`python -m pip install -r .\requirements.txt`

## Migrate database

`alembic revision -m "REVISION NAME" --autogenerate`

`alembic upgrade head`

## Testing code

Running unittests

`pytest`

- `--tb=no` no error stacktraces
- `--disable-warnings` no warnings
- `-s` enable printing

Checking test coverage

`coverage run -m pytest`

`coverage html`

or

`pytest --cov=app --cov=api --cov-report=html --cov-fail-under=85`
