FROM python:3.11-slim

WORKDIR /neuralk

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY ml.py .
COPY worker.py .
COPY config.py .
COPY logger.py .

COPY deploy/docker/server/.env .

EXPOSE 8080

CMD ["python", "server.py"]
