# Kubernetes Deployment Guide for Neuralk ML API

This directory contains Kubernetes manifests for deploying the Neuralk ML API service in a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster, for dev and testing purposes, a local cluster like Minikube.
- kubectl configured to connect to your cluster
- Container registry with your built Docker images
- Storage class available for persistent volumes

## Components

1. **00-namespace.yaml**: Creates the `neuralk` namespace
2. **01-configmap.yaml**: Environment configuration for all services
3. **02-secrets.yaml**: Sensitive credentials (MinIO access keys)
4. **03-persistent-volumes.yaml**: Persistent volume claims for Redis and MinIO
5. **04-redis.yaml**: Redis deployment and service
6. **05-minio.yaml**: MinIO deployment and service
7. **06-init-minio.yaml**: Job to initialize MinIO buckets
8. **07-worker.yaml**: ML worker deployment
9. **08-server.yaml**: API server deployment and service
10. **09-ingress.yaml**: Ingress for external access
11. **10-hpa.yaml**: Horizontal Pod Autoscaler for workers

## Deployment

Run:

```bash
kubectl apply -f deploy/kube/
```

## Monitoring

You can monitor the workers and server logs:

```bash
kubectl -n neuralk logs deployment/server
kubectl -n neuralk logs deployment/worker
```

To get the Minio console URL, you can port-forward the MinIO service:

```bash
kubectl -n neuralk port-forward service/minio 9001:9001
```

Then access the MinIO console at [http://localhost:9001](http://localhost:9001) using the credentials defined in `02-secrets.yaml`.

Or use Minikube to bind the serveice to localhost and a random port:

```bash
minikube service minio -n neuralk
```

## Cleanup

To remove all resources:

```bash
kubectl delete namespace neuralk
```

## Using the Helm Chart

For a more flexible and parameterized deployment across different environments (development, staging, production), we recommend using the Helm chart located in the `../helm/neuralk` directory.

The Helm chart provides:

- Environment-specific configurations
- Automatic resource allocation based on environment
- TLS configuration for secure access
- Simplified deployment and upgrades
- Worker autoscaling based on load

To deploy using the Helm chart:

```bash
# For development environment
helm install neuralk ./deploy/helm/neuralk -f ./deploy/helm/neuralk/values-dev.yaml --create-namespace -n neuralk-dev
```

For more details, see [../helm/neuralk/README.md](../helm/neuralk/README.md).
