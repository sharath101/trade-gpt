FROM python:3.9-slim

COPY TradeCore /TradeCore

RUN pip install -r /TradeCore/requirements.txt

COPY StrategEase/requirements.txt /StrategEase/requirements.txt

COPY StrategEase/main.py /StrategEase/main.py 

WORKDIR /StrategEase

RUN pip install -r requirements.txt

WORKDIR /StrategEase/app

COPY StrategEase/app .

ENV PYTHONPATH=/TradeCore:$PYTHONPATH

WORKDIR /StrategEase

ENTRYPOINT ["python", "main.py"]
