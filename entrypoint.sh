#!/bin/bash

# Run alembic upgrade head
alembic upgrade head

# Start the FastAPI server
python main.py