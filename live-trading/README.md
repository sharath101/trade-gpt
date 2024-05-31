# trade-src

## Run

### In the root directiory

```
python -m venv venv
source venv/bin/activate
pip install -r trade-src/requirements.txt
cd trade-src
python main.py
```

## Launching Docker for Strategies

### Set envirnment variables

```
export DOCKER_HOST=tcp://<address>:<port>
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=/path/to/your/certs
```
```
export DOCKER_HOST=tcp://192.168.1.100:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=/path/to/your/certs

```

> sudo docker system prune