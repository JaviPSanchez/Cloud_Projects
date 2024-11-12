# Use the tiangolo/uvicorn-gunicorn-fastapi image as a base
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Copy the requirements file and install dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --requirement /tmp/requirements.txt

# Copy the FastAPI application code
COPY ./app /app

# Expose port 8080
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


