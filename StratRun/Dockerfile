FROM python:3.12-slim

COPY TradeCore /TradeCore

RUN pip install -r /TradeCore/requirements.txt

COPY StratRun/requirements.txt /StratRun/requirements.txt

COPY StratRun/main.py /StratRun/main.py

WORKDIR /StratRun

RUN pip install -r requirements.txt

WORKDIR /StratRun/app

COPY StratRun/app .

ENV PYTHONPATH=/TradeCore:$PYTHONPATH

WORKDIR /StratRun

ENTRYPOINT ["python", "main.py"]