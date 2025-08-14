FROM python:3.11-slim

WORKDIR /neuralk

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .
COPY ml.py .
COPY config.py .
COPY logger.py .

COPY deploy/docker/worker/.env .

ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

CMD ["python", "worker.py"]
