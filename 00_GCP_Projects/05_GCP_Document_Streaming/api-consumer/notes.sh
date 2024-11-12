# Run Docker local
docker compose up

# Open my Docker Hub
https://hub.docker.com/r/javipsanchez/fastapi
# Build image
docker build -t javipsanchez/fastapi-consumer:latest .
# Docker Login
docker login
# Push the Image to Docker Hub:
docker push javipsanchez/fastapi-consumer:latest

