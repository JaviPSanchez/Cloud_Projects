# Use the tiangolo/uvicorn-gunicorn-fastapi image as a base
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Copy the requirements file and install dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --requirement /tmp/requirements.txt

# Copy the FastAPI application code
COPY ./app /app

# Ensure the container listens on the dynamic Cloud Run port
ENV PORT=8080


