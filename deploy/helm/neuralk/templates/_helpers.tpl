{{/*
Expand the name of the chart.
*/}}
{{- define "neuralk.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "neuralk.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "neuralk.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "neuralk.labels" -}}
helm.sh/chart: {{ include "neuralk.chart" . }}
{{ include "neuralk.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.global.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "neuralk.selectorLabels" -}}
app.kubernetes.io/name: {{ include "neuralk.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "neuralk.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "neuralk.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Return the proper image tag
*/}}
{{- define "neuralk.imageTag" -}}
{{- .Values.image.tag | default .Values.global.imageTag | default .Chart.AppVersion -}}
{{- end -}}

{{/*
Return the proper Docker Image Registry
*/}}
{{- define "neuralk.imageRegistry" -}}
{{- .Values.image.registry | default .Values.global.registry -}}
{{- end -}}

{{/*
Return the proper image name
*/}}
{{- define "neuralk.imageName" -}}
{{- $registryName := include "neuralk.imageRegistry" . -}}
{{- $repositoryName := .Values.image.repository -}}
{{- $tag := include "neuralk.imageTag" . -}}
{{- if $registryName -}}
    {{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}

{{/*
Return the proper Server image name
*/}}
{{- define "neuralk.server.image" -}}
{{- $registryName := .Values.server.image.registry | default .Values.global.registry -}}
{{- $repositoryName := .Values.server.image.repository -}}
{{- $tag := .Values.server.image.tag | default .Values.global.imageTag | default .Chart.AppVersion -}}
{{- if $registryName -}}
    {{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}

{{/*
Return the proper Worker image name
*/}}
{{- define "neuralk.worker.image" -}}
{{- $registryName := .Values.worker.image.registry | default .Values.global.registry -}}
{{- $repositoryName := .Values.worker.image.repository -}}
{{- $tag := .Values.worker.image.tag | default .Values.global.imageTag | default .Chart.AppVersion -}}
{{- if $registryName -}}
    {{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}

{{/*
Return the proper Client image name
*/}}
{{- define "neuralk.client.image" -}}
{{- $registryName := .Values.client.image.registry | default .Values.global.registry -}}
{{- $repositoryName := .Values.client.image.repository -}}
{{- $tag := .Values.client.image.tag | default .Values.global.imageTag | default .Chart.AppVersion -}}
{{- if $registryName -}}
    {{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}

{{/*
Return the proper Redis image name
*/}}
{{- define "neuralk.redis.image" -}}
{{- $registryName := .Values.redis.image.registry | default .Values.global.registry -}}
{{- $repositoryName := .Values.redis.image.repository -}}
{{- $tag := .Values.redis.image.tag | default "alpine" -}}
{{- if $registryName -}}
    {{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}

{{/*
Return the proper MinIO image name
*/}}
{{- define "neuralk.minio.image" -}}
{{- $registryName := .Values.minio.image.registry | default .Values.global.registry -}}
{{- $repositoryName := .Values.minio.image.repository -}}
{{- $tag := .Values.minio.image.tag | default "latest" -}}
{{- if $registryName -}}
    {{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}
