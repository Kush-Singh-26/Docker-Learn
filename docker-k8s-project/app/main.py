import os
from fastapi import FastAPI
from redis import Redis

app = FastAPI()

# Connect to Redis. The hostname 'redis' will be provided by
# Docker Compose or Kubernetes.
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
db = Redis(host=redis_host, port=redis_port, decode_responses=True)

# Get the greeting message from an environment variable
greeting = os.getenv("GREETING", "Hello")

@app.get("/")
def read_root():
    try:
        # Increment the 'hits' counter in Redis
        hits = db.incr("hits")
    except Exception as e:
        # Handle connection errors gracefully
        return {"error": str(e), "message": "Failed to connect to Redis."}

    return {"message": f"{greeting}! You have visited this page {hits} times."}