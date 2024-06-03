FROM python:3.9-slim

COPY TradeCore /TradeCore

RUN pip install -r /TradeCore/requirements.txt

COPY Backtestify/requirements.txt /Backtestify/requirements.txt

WORKDIR /Backtestify

RUN pip install -r requirements.txt

WORKDIR /Backtestify/app

COPY Backtestify/app .

ENV PYTHONPATH=/TradeCore:$PYTHONPATH

ENTRYPOINT [ "/bin/bash" ]
