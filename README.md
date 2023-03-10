# MealMatch backend repository

Boilerplate from [teamhide](https://github.com/teamhide/fastapi-boilerplate).

## To run the project

`python -m virualenv venv`

`.\venv\Scripts\activate`

`python -m pip install -r .\requirements.txt`

## Migrate database

`alembic revision -m "REVISION NAME" --autogenerate`

`alembic upgrade head`
