# neuralk-technical-assessment

Neuralk AI Technical Assessment - DevOps / SRE

## Architecture Diagram

```mermaid
graph TD
    %% Define Client interactions
    Client([Client]) --> |1. Upload dataset| Server
    Client --> |3. Request model training| Server
    Client --> |5. Upload test data| Server
    Client --> |7. Request prediction| Server
    Client --> |9. Download results| Server
    Client --> |Check job status| Server
    
    %% Define Server component
    subgraph Server["Web Server (server.py)"]
        Upload["/upload endpoint"]
        Fit["/fit endpoint"]
        Predict["/predict endpoint"]
        Status["/status endpoint"]
        Result["/result endpoint"]
    end
    
    %% Define Storage component
    subgraph MinIO["Object Storage (MinIO)"]
        Datasets[("datasets bucket")]
        Models[("models bucket")]
        Results[("results bucket")]
    end
    
    %% Define Queue and Workers
    subgraph Redis["Task Queue (Redis)"]
        Queue[("RQ Queue")]
    end
    
    subgraph Workers["RQ Workers (worker.py)"]
        Worker1["Worker 1"]
        Worker2["Worker 2"]
        WorkerN["Worker N..."]
    end
    
    %% Define ML component
    subgraph ML["Machine Learning (ml.py)"]
        FitFunc["fit()"]
        PredictFunc["predict()"]
    end
    
    %% Define flow from server to storage
    Upload --> |2. Generate presigned URL| Datasets
    Fit --> |4. Enqueue fit job| Queue
    Predict --> |8. Enqueue predict job| Queue
    Result --> |10. Generate download URL| Results
    Status --> |Query job status| Queue
    
    %% Define worker interactions
    Queue --> |Dispatch job| Workers
    Workers --> |Execute| ML
    
    %% Define ML interactions with storage
    FitFunc --> |Read training data| Datasets
    FitFunc --> |Write model| Models
    PredictFunc --> |Read test data| Datasets
    PredictFunc --> |Read model| Models
    PredictFunc --> |Write results| Results
```

## Project Description

This project implements a machine learning API service that allows users to:

1. Upload datasets
2. Train models on those datasets
3. Make predictions using trained models
4. Download prediction results

The application consists of the following components:

- A web server (`server.py`) that handles API requests
- MinIO object storage for datasets, models, and results
- Redis and RQ for task queueing and processing
- RQ workers that execute the machine learning tasks
- ML functions (`ml.py`) containing the core functionality for model training and prediction
- A client interface (`client.py`) for interacting with the API

Example workflows are provided in `example_1.py` (complete training and prediction workflow) and `example_2.py` (parallel model training).

## Configuration with .env Files

The project uses dotenv files for configuration. To set up your environment:

1. Create a `.env` file, if not already present:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your specific settings:
   - Server configuration (host, port)
   - Redis connection settings
   - MinIO configuration
   - Logging preferences
   - Queue settings

You can also create a `.env.local` file for overrides that shouldn't be committed to version control.

Available configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| SERVER_HOST | Host for the web server | localhost |
| SERVER_PORT | Port for the web server | 8080 |
| REDIS_HOST | Redis server host | localhost |
| REDIS_PORT | Redis server port | 6379 |
| REDIS_DB | Redis database number | 0 |
| REDIS_PASSWORD | Redis password (if required) | None |
| MINIO_HOST | MinIO server host and port | localhost:9000 |
| MINIO_ACCESS_KEY | MinIO access key | minioadmin |
| MINIO_SECRET_KEY | MinIO secret key | minioadmin |
| MINIO_SECURE | Whether to use HTTPS for MinIO | False |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| JOB_TIMEOUT | RQ job timeout | 600s |
| MAX_RETRIES | Maximum retries for failed jobs | 4 |
| QUEUE_NAME | Name of the RQ queue | default |
