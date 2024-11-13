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

# To test if your Kafka is running correctly:

# 1) Connect to the container CLI and go to the Kafka directory
# Go inside CLI of Kafka
docker exec -it 05_gcp_document_streaming-kafka-1 bash
# Go to main folder to setup topics
cd /opt/bitnami/kafka/bin

# 2) List Existing Topics
./kafka-topics.sh --list --bootstrap-server localhost:9092

# 3) Create Topic
./kafka-topics.sh --create --topic TOPIC_NAME --bootstrap-server localhost:9092
./kafka-topics.sh --create --topic ingestion-topic --bootstrap-server localhost:9092

# 4) Connect with a second cli to the container and create a producer message
./kafka-console-producer.sh --bootstrap-server <kafka-broker> --topic <topic-name>
./kafka-console-producer.sh --bootstrap-server localhost:9092 --topic ingestion-topic
# 5) Type in to the producer cli a message and hit enter
# It will let us write messages:
> This is a message
> Another message

# 6) Check if you can see the message in the consumer cli (open a second CLI)
# Listen to messages (consume messages)
./kafka-console-consumer.sh --bootstrap-server <kafka-broker> --topic <topic-name> --from-beginning
./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic ingestion-topic --from-beginning


