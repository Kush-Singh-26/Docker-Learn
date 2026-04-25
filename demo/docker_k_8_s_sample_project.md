# Docker + Kubernetes Hands-on Project (FastAPI version)

This version replaces the backend with **Python FastAPI**, while keeping the same Docker, Docker Compose, and Kubernetes setup — so you can compare with the Go example.

---

## Overview

This project demonstrates the same core topics:

* Multi-stage Docker builds
* Docker networking
* Docker Compose
* Kubernetes: Deployment, Services, Env vars, Scaling, Storage

The FastAPI server stores a counter in `/data/counter.txt`, reads configuration from env vars, and responds with a JSON payload.

---

## Folder structure

```
project/
├─ app/
│  ├─ main.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ docker-compose.yml
├─ .env
└─ k8s/
   ├─ namespace.yaml
   ├─ cm-secret.yaml
   ├─ deployment.yaml
   ├─ service-nodeport.yaml
   ├─ pvc-pv.yaml
   └─ hpa.yaml
```

---

## `app/main.py`

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI()

STORAGE_PATH = os.getenv("STORAGE_PATH", "/data")
MESSAGE = os.getenv("MESSAGE", "Hello from FastAPI container")
COUNTER_FILE = os.path.join(STORAGE_PATH, "counter.txt")

os.makedirs(STORAGE_PATH, exist_ok=True)

# Load counter
try:
    with open(COUNTER_FILE, "r") as f:
        counter = int(f.read().strip())
except Exception:
    counter = 0

@app.get("/")
def read_root():
    global counter
    counter += 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(counter))

    hostname = os.uname()[1]
    return JSONResponse({
        "message": MESSAGE,
        "hostname": hostname,
        "counter": counter
    })
```

---

## `app/requirements.txt`

```
fastapi==0.115.2
uvicorn==0.32.0
```

---

## `app/Dockerfile` (multi-stage build)

```dockerfile
# Stage 1: build base
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PORT=3000
EXPOSE 3000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
```

### Explanation

* **Stage 1** installs dependencies separately (so runtime image stays smaller).
* **Stage 2** copies only the installed packages and app code.
* Final image is small (~150MB) compared to single-stage builds.

---

## `.env`

```
MESSAGE=Hello from FastAPI Compose
PORT=3000
```

---

## `docker-compose.yml`

```yaml
version: '3.8'
services:
  web:
    build: ./app
    image: toy-counter-fastapi:local
    environment:
      - MESSAGE=${MESSAGE}
    ports:
      - "8080:3000"
    volumes:
      - counter-data:/data
    networks:
      - front-tier

networks:
  front-tier:
    driver: bridge

volumes:
  counter-data:
```

---

## Kubernetes manifests (reuse from Go example)

Update only the Deployment image and name:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: toy-counter-fastapi
  namespace: demo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: toy-counter-fastapi
  template:
    metadata:
      labels:
        app: toy-counter-fastapi
    spec:
      containers:
        - name: toy-counter-fastapi
          image: toy-counter-fastapi:local
          ports:
            - containerPort: 3000
          envFrom:
            - configMapRef:
                name: app-config
          env:
            - name: SECRET_TOKEN
              valueFrom:
                secretKeyRef:
                  name: app-secret
                  key: SECRET_TOKEN
          volumeMounts:
            - name: counter-storage
              mountPath: /data
      volumes:
        - name: counter-storage
          persistentVolumeClaim:
            claimName: demo-pvc
```

---

## Running & testing step-by-step

### 1. Build & run locally with Docker Compose

```bash
docker compose up --build
```

Visit [http://localhost:8080](http://localhost:8080) — you’ll see JSON output:

```json
{"message": "Hello from FastAPI container", "hostname": "web-1", "counter": 5}
```

Each refresh increments the counter stored in `/data`.

### 2. Scale containers

```bash
docker compose up --scale web=3 -d
```

Multiple containers now share the same Docker volume.

### 3. Run on Kubernetes

```bash
# Build image
docker build -t toy-counter-fastapi:local ./app
minikube image load toy-counter-fastapi:local

# Deploy
kubectl apply -f k8s/
```

Then open the service:

```bash
minikube service toy-counter-svc -n demo-app --url
```

---

## Explanation of key concepts

| Concept                   | FastAPI Example                                                        |
| ------------------------- | ---------------------------------------------------------------------- |
| **Multi-stage build**     | Python dependencies installed in builder stage, copied to slim runtime |
| **Docker networking**     | Compose automatically creates an isolated bridge network               |
| **Compose orchestration** | One YAML defines environment, volumes, ports, networks                 |
| **K8s Deployment**        | Declarative desired state for pods                                     |
| **Service**               | Stable endpoint for load balancing across pods                         |
| **Env vars**              | Injected from `.env` (Compose) or ConfigMap/Secret (K8s)               |
| **Scaling**               | `docker compose up --scale` or `kubectl scale deploy`                  |
| **Storage**               | Data persists via Docker volumes or K8s PVC/PV                         |

---

## Optional extensions

* Add a `/health` route to integrate readiness/liveness probes.
* Use Redis or PostgreSQL instead of the file-based counter.
* Add GitHub Actions workflow for CI/CD to build and deploy.

---

## License

Free for educational and personal use.
