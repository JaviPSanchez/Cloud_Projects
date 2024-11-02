# Open my Docker Hub
https://hub.docker.com/r/javipsanchez/fastapi
# Build image
docker build -t javipsanchez/fastapi:latest .
# Docker Login
docker login
# Push the Image to Docker Hub:
docker push javipsanchez/fastapi:latest

