FROM python:3.11-slim

WORKDIR /neuralk

RUN apt-get update && apt-get install -y curl && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/api/ src/api/
COPY src/utils/ src/utils/
COPY src/core/ src/core/

ENV PYTHONPATH="${PYTHONPATH}:/neuralk/src/api:/neuralk/src/utils:/neuralk/src/core"

EXPOSE 8080

CMD ["python", "src/api/server.py"]
