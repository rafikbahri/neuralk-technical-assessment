FROM python:3.11-slim

WORKDIR /neuralk

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/api/ src/api/
COPY src/utils/ src/utils/
COPY src/core/ src/core/

COPY deploy/docker/server/.env .

ENV PYTHONPATH="${PYTHONPATH}:/neuralk/src/api:/neuralk/src/utils:/neuralk/src/core"

EXPOSE 8080

CMD ["python", "src/api/server.py"]
