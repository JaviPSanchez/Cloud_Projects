# Launch FastAPI (From root folder) to run locally
uvicorn app.main:app --reload --port <port>

# Run Docker Compose under the same network
docker-compose up --build

# Browser:
http://localhost:8001/
http://localhost:8001/customer
# Run Docs
http://localhost:8001/docs


# Go inside CLI of Kafka
docker exec -it 05_gcp_document_streaming-kafka-1 bash
# Go to main folder to setup topics
cd /opt/bitnami/kafka/bin

# List Topics
./kafka-topics.sh --list --bootstrap-server localhost:9092

## Create Topic
./kafka-topics.sh --create --topic ingestion-topic --bootstrap-server localhost:9092
./kafka-topics.sh --create --topic spark-output --bootstrap-server localhost:9092


# Local consumer
./kafka-console-consumer.sh --topic ingestion-topic --bootstrap-server localhost:9092
./kafka-console-consumer.sh --topic spark-output --bootstrap-server localhost:9092


# Local producer 
./kafka-console-producer.sh --topic ingestion-topic --bootstrap-server localhost:9092

# To test if your Kafka is running correctly:
1. Connect to the container cli and go to the Kafka directory
2. Start a local consumer
3. Connect with a second cli to the container
4. Start in the second cli a local producer
5. Type in to the producer cli a message and hit enter
6. Check if you can see the message in the consumer cli