# --- Stage 1: The Builder ---
# Use a full Python image to build our dependencies
FROM python:3.10-slim AS builder

# Set the working directory
WORKDIR /usr/src/app

# Install build dependencies
RUN pip install --upgrade pip

# Copy and install Python requirements
COPY ./app/requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/usr/src/app/wheels -r requirements.txt


# --- Stage 2: The Final Image ---
# Use a slim image for the final container
FROM python:3.10-slim

WORKDIR /usr/src/app

# Copy the pre-built wheels from the builder stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Install the dependencies from the local wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Copy our application code
COPY ./app /usr/src/app/

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]