FROM python:3.12

# Preload python packages required
RUN pip install pytest black mypy pylint

WORKDIR /ttex
COPY setup.py setup.py
COPY ttex ttex

# Launcher script
COPY launch.sh launch.sh

RUN pip install -e .

WORKDIR /tests
