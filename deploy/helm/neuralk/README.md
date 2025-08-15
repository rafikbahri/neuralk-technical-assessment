# neuralk

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.0.0](https://img.shields.io/badge/AppVersion-1.0.0-informational?style=flat-square)

A Helm chart for Neuralk ML API

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Neuralk Team | <team@neuralk.ai> |  |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| client.enabled | bool | `true` |  |
| client.image.repository | string | `"rafik08/neuralk-client"` |  |
| client.image.tag | string | `""` |  |
| client.replicaCount | int | `1` |  |
| client.resources.limits.cpu | string | `"200m"` |  |
| client.resources.limits.memory | string | `"256Mi"` |  |
| client.resources.requests.cpu | string | `"100m"` |  |
| client.resources.requests.memory | string | `"128Mi"` |  |
| config.jobTimeout | string | `"600s"` |  |
| config.logLevel | string | `"INFO"` |  |
| config.maxRetries | int | `4` |  |
| config.queueName | string | `"default"` |  |
| global.commonAnnotations | object | `{}` |  |
| global.commonLabels | object | `{}` |  |
| global.environment | string | `"dev"` |  |
| global.imagePullPolicy | string | `"Always"` |  |
| global.imagePullSecrets | list | `[]` |  |
| global.imageTag | string | `"latest"` |  |
| global.registry | string | `""` |  |
| ingress.annotations."kubernetes.io/ingress.class" | string | `"nginx"` |  |
| ingress.annotations."nginx.ingress.kubernetes.io/ssl-redirect" | string | `"false"` |  |
| ingress.className | string | `"nginx"` |  |
| ingress.enabled | bool | `true` |  |
| ingress.hosts.minio.host | string | `"minio.neuralk.local"` |  |
| ingress.hosts.minio.paths[0].path | string | `"/"` |  |
| ingress.hosts.minio.paths[0].pathType | string | `"Prefix"` |  |
| ingress.hosts.minio.paths[0].port | int | `9001` |  |
| ingress.hosts.server.host | string | `"api.neuralk.local"` |  |
| ingress.hosts.server.paths[0].path | string | `"/"` |  |
| ingress.hosts.server.paths[0].pathType | string | `"Prefix"` |  |
| ingress.tls | list | `[]` |  |
| minio.buckets[0].name | string | `"datasets"` |  |
| minio.buckets[1].name | string | `"models"` |  |
| minio.buckets[2].name | string | `"results"` |  |
| minio.credentials.accessKey | string | `"minioadmin"` |  |
| minio.credentials.secretKey | string | `"minioadmin"` |  |
| minio.enabled | bool | `true` |  |
| minio.image.repository | string | `"minio/minio"` |  |
| minio.image.tag | string | `"latest"` |  |
| minio.persistence.enabled | bool | `true` |  |
| minio.persistence.size | string | `"10Gi"` |  |
| minio.persistence.storageClass | string | `""` |  |
| minio.resources.limits.cpu | string | `"300m"` |  |
| minio.resources.limits.memory | string | `"512Mi"` |  |
| minio.resources.requests.cpu | string | `"200m"` |  |
| minio.resources.requests.memory | string | `"256Mi"` |  |
| minio.service.apiPort | int | `9000` |  |
| minio.service.consolePort | int | `9001` |  |
| namespace.create | bool | `true` |  |
| namespace.name | string | `"neuralk-dev"` |  |
| redis.configuration.appendOnly | string | `"yes"` |  |
| redis.configuration.appendfsync | string | `"everysec"` |  |
| redis.enabled | bool | `true` |  |
| redis.image.repository | string | `"redis"` |  |
| redis.image.tag | string | `"alpine"` |  |
| redis.persistence.enabled | bool | `true` |  |
| redis.persistence.size | string | `"1Gi"` |  |
| redis.persistence.storageClass | string | `""` |  |
| redis.resources.limits.cpu | string | `"200m"` |  |
| redis.resources.limits.memory | string | `"256Mi"` |  |
| redis.resources.requests.cpu | string | `"100m"` |  |
| redis.resources.requests.memory | string | `"128Mi"` |  |
| redis.service.port | int | `6379` |  |
| server.enabled | bool | `true` |  |
| server.image.repository | string | `"rafik08/neuralk-server"` |  |
| server.image.tag | string | `""` |  |
| server.replicaCount | int | `1` |  |
| server.resources.limits.cpu | string | `"300m"` |  |
| server.resources.limits.memory | string | `"512Mi"` |  |
| server.resources.requests.cpu | string | `"200m"` |  |
| server.resources.requests.memory | string | `"256Mi"` |  |
| server.service.port | int | `8080` |  |
| server.service.type | string | `"ClusterIP"` |  |
| worker.autoscaling.enabled | bool | `true` |  |
| worker.autoscaling.maxReplicas | int | `10` |  |
| worker.autoscaling.minReplicas | int | `2` |  |
| worker.autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| worker.enabled | bool | `true` |  |
| worker.image.repository | string | `"rafik08/neuralk-worker"` |  |
| worker.image.tag | string | `""` |  |
| worker.replicaCount | int | `2` |  |
| worker.resources.limits.cpu | string | `"500m"` |  |
| worker.resources.limits.memory | string | `"512Mi"` |  |
| worker.resources.requests.cpu | string | `"250m"` |  |
| worker.resources.requests.memory | string | `"256Mi"` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
