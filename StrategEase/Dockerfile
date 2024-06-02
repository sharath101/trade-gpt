FROM python:3.9-slim

COPY TradeCore /TradeCore

RUN pip install -r /TradeCore/requirements.txt

COPY StrategEase/requirements.txt /StrategEase/requirements.txt

WORKDIR /StrategEase

RUN pip install -r requirements.txt

WORKDIR /StrategEase/app

COPY StrategEase/app .

# CMD ["python", "app/main.py"]

ENV PYTHONPATH=/TradeCore:$PYTHONPATH

ENTRYPOINT [ "/bin/bash" ]
