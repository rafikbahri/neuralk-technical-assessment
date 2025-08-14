# DEV ONLY
FROM python:3.11-slim

WORKDIR /neuralk

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY client.py .
COPY config.py .
COPY logger.py .
COPY make_data.py .
COPY example_*.py .

COPY deploy/docker/client/.env .

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app/data

ENTRYPOINT ["tail", "-f", "/dev/null"]