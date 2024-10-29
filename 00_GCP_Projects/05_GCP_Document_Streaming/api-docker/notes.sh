# Build image
docker build -t javipsanchez/fastapi:v6 .
# Docker Login
docker login
# Push the Image to Docker Hub:
docker push javipsanchez/fastapi:v6

