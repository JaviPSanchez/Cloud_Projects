# Built-in
import os
import threading
import sys
from fastapi import FastAPI
import uvicorn

# Logger
from loguru import logger
from logging_config import configure_logger

# Kafka
if sys.version_info >= (3, 12, 0):
    import six
    sys.modules['kafka.vendor.six.moves'] = six.moves
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Configure logging
configure_logger()

# Initialize FastAPI
app = FastAPI()

def consume_kafka_messages():
    consumer = None
    try:
        logger.info("Attempting to create Kafka consumer...")

        # Create Kafka consumer in GCP
        consumer = KafkaConsumer(
            'ingestion-topic',
            bootstrap_servers='10.128.0.14:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-consumer-group',
            value_deserializer=lambda x: x.decode('utf-8')
        )
        logger.info("Kafka consumer created successfully. Listening for messages...")

        # Listen for messages on the topic
        for message in consumer:
            logger.info(f"Received message: {message.value}")
    
    except KafkaError as e:
        logger.error(f"Failed to consume message from Kafka: {e}")
    except Exception as e:
        logger.error(f"An error occurred while consuming Kafka messages: {e}")
    finally:
        if consumer is not None:
            consumer.close()  # Close the consumer if it was created
            logger.info("Kafka consumer closed.")

# Start Kafka consumer in a background thread when the app starts
@app.on_event("startup")
def startup_event():
    threading.Thread(target=consume_kafka_messages, daemon=True).start()

# Simple health check endpoint
@app.get("/")
def read_root():
    return {"status": "Kafka consumer is running"}

# Run the FastAPI application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
