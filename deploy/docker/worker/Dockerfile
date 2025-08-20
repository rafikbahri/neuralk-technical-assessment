FROM python:3.11-slim

WORKDIR /neuralk

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/api/ src/api/
COPY src/utils/ src/utils/
COPY src/core/ src/core/

ENV PYTHONPATH="${PYTHONPATH}:/neuralk/src/"

CMD ["python", "src/core/worker.py"]
