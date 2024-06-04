FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV SYMBOL "SBIN"
ENV BALANCE "20000"
ENV SOCKET_URL "http://host.docker.internal:5000"

ENTRYPOINT [ "python", "main.py" ]