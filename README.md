# Docker & Kubernetes Learning Project

A hands-on project for learning Docker containerization and Kubernetes orchestration.

## Project Structure

```
kube_learn/
├── config.yaml                    # Kind cluster configuration
├── demo/                         # Basic Docker demo
│   ├── backend/                  # Python FastAPI app
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── frontend/                # Static HTML with nginx
│   │   ├── index.html
│   │   └── nginx.conf
│   ├── docker-compose.yaml      # Compose for local dev
│   └── docker_k_8_s_sample_project.md
└── docker-k8s-project/           # Full K8s project
    ├── app/                      # FastAPI app with Redis
    │   ├── main.py
    │   └── requirements.txt
    ├── k8s/                      # Kubernetes manifests
    │   ├── 01-redis-pvc.yml      # PersistentVolumeClaim
    │   ├── 02-app-configmap.yml  # ConfigMap
    │   ├── 03-redis-deployment.yml
    │   ├── 04-redis-service.yml
    │   ├── 05-app-deployment.yml
    │   └── 06-app-service.yml
    ├── Dockerfile
    ├── docker-compose.yml
    ├── kind-config.yml           # 3-node Kind cluster
    └── notes.md
```

## Quick Start

### Local Development with Docker Compose

**Demo project:**
```bash
cd demo
docker-compose up --build
```

**Full K8s project:**
```bash
cd docker-k8s-project
docker-compose up --build
```

### Kubernetes with Kind

**Create cluster:**
```bash
kind create cluster --config kind-config.yml
```

**Deploy app:**
```bash
kubectl apply -f docker-k8s-project/k8s/
```

**Check deployment:**
```bash
kubectl get all -l app=docker-k8s-project
```

## Prerequisites

- Docker & Docker Compose
- Kubernetes (kubectl)
- Kind (for local K8s)
- Python 3.10+

## Endpoints

| Service | URL |
|---------|-----|
| Demo backend | http://localhost:8000/hello |
| K8s app backend | http://localhost:8000 |
| Kind cluster nodes | `kind get clusters` |