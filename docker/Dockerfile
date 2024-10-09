FROM python:3.12

# Preload python packages required
RUN pip install pytest black mypy pylint

WORKDIR /ttex
COPY setup.py setup.py
COPY ttex ttex

RUN pip install -e .

WORKDIR /tests
