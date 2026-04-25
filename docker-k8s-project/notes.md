🐳 Docker Concepts
1. Multi-Stage Build
What it is: A technique using multiple FROM instructions in a single Dockerfile. Each FROM instruction begins a new "stage."

Purpose: To create a final production image that is as small and secure as possible.

How it works:

Stage 1 (The "Builder"): You use a full-sized image (e.g., python:3.10) that contains all the build tools, compilers, and development dependencies. In this stage, you compile your code or install your dependencies.

Stage 2 (The "Final" Image): You start from a fresh, minimal base image (e.g., python:3.10-slim). You then use the COPY --from=builder ... command to copy only the essential compiled code or packages from Stage 1.

Benefit: The final image doesn't contain any of the build tools or development libraries, making it smaller to download and reducing its potential security attack surface.

2. Docker Networking
What it is: The system that allows Docker containers to communicate with each other and the outside world.

Purpose: To isolate applications and provide a simple way for containers in the same application to find each other.

How it works (with Docker Compose):

When you run docker-compose up, Compose automatically creates a private virtual network.

It attaches all services (containers) defined in your docker-compose.yml file to this single network.

The key feature is service discovery: Docker provides an internal DNS. This allows any container to find any other container on the network simply by using its service name as a hostname.

Example: Our backend container was able to find the redis container at the hostname redis (which we set in the REDIS_HOST environment variable).

3. Docker Compose
What it is: A tool for defining and running multi-container Docker applications.

Purpose: To easily manage a complete application stack (e.g., web server, database, cache) on a single machine, primarily for local development.

How it works:

You define all your application's components (called services) in a single YAML file: docker-compose.yml.

This file also defines the networks they share and the volumes they use for data persistence.

A single command (docker-compose up) reads this file, builds the images (if needed), creates the network, and starts all the containers in the correct order.

📦 Kubernetes (K8s) Concepts
1. Storage / Volumes
Problem: Containers are ephemeral. Their filesystems are deleted when the container is removed. This is bad for databases.

K8s Solution: A two-part system for persistent data:

PersistentVolume (PV): A piece of storage in the cluster (like a physical disk or network drive). Think of this as the "supply" of storage.

PersistentVolumeClaim (PVC): A request for storage by an application (e.g., "I need 1Gi of storage"). This is the "demand" for storage.

How it works:

You create a PVC (01-redis-pvc.yml) asking for storage.

Kubernetes finds a PV that matches the request and "binds" them together. (In kind and Minikube, this is handled automatically).

Your Deployment (03-redis-deployment.yml) references the claimName: redis-pvc in its volumes section. This tells the Pod to mount that persistent storage at a specific path (e.g., /data).

Benefit: Your Redis data now lives in the PVC, separate from the Pod. If the Redis Pod crashes or is redeployed, the new Pod just re-mounts the same PVC and all the data is still there.

2. Env Var (via ConfigMap)
What it is: A ConfigMap is a Kubernetes object used to store non-confidential configuration data as key-value pairs.

Purpose: To decouple configuration from your application's image. This allows you to change your app's settings without rebuilding the Docker image.

How it works:

You create a ConfigMap (02-app-configmap.yml) with your settings (e.g., REDIS_HOST: redis-service).

In your Deployment (05-app-deployment.yml), you use envFrom to tell Kubernetes to load all key-value pairs from that ConfigMap and inject them into the container as environment variables.

Benefit: Your application code (main.py) can read these settings (e.g., os.getenv("REDIS_HOST")) in a standard way, but the values themselves are managed by Kubernetes.

3. Deployment
What it is: A Kubernetes resource that provides a "desired state" for your application.

Purpose: To manage a set of identical Pods (ReplicaSet), ensuring that a specified number of them are always running. It's the standard way to run stateless applications.

Key Features:

Desired State: You tell the Deployment you want replicas: 2 of your app. Kubernetes's job is to make sure 2 Pods are always running.

Self-Healing: If a Pod crashes, the Deployment's ReplicaSet detects it and automatically creates a new one to replace it.

Rolling Updates: When you update your Deployment (e.g., with a new image tag), it updates the Pods one by one, ensuring zero downtime.

Template: It contains a template section, which is a blueprint for how to create each Pod (what image to use, what ports to open, what ConfigMaps to use, etc.).

4. Service
What it is: A Kubernetes resource that acts as a stable network endpoint (a "front desk") for a set of Pods.

Problem: Pods are ephemeral. They get new IP addresses every time they are created or restarted. A Deployment might manage 5 identical Pods, each with a different IP. How do other Pods (or you) reliably connect to them?

Solution (How it works):

A Service gets a single, stable internal DNS name (e.g., redis-service).

It uses a selector (e.g., app: redis) to find all running Pods that have that label.

It acts as an internal load balancer, distributing network traffic among all the matching Pods.

Key Types:

ClusterIP: (Default) Creates an internal-only IP. This is perfect for backend communication (e.g., your app-deployment talking to your redis-service).

NodePort: Exposes the service on a static port on every node in your cluster. This is a simple way to get external traffic into your cluster, which we used (nodePort: 30007).

5. Scaling
What it is: The process of changing the number of running replicas (Pods) for a Deployment to match the current load.

Purpose: To handle increases (scale-out) or decreases (scale-in) in application traffic.

How it works:

It's as simple as changing the replicas field in your Deployment's YAML file.

The command kubectl scale deployment app-deployment --replicas=5 is a shortcut that does this for you.

The Deployment controller sees the "desired state" (5 replicas) doesn't match the "current state" (e.g., 2 replicas) and creates 3 new Pods.

Benefit: This is incredibly powerful. The Service (app-service) automatically detects these new Pods (because they match its selector) and starts load-balancing traffic to them immediately, with no manual configuration.