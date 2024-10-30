# You need this to use FastAPI, work with statuses and be able to end HTTPExceptions
from fastapi import FastAPI, Request, HTTPException, status

# You need this to be able to turn classes into JSONs and return
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Needed for json.dumps
import json

# Logging
from loguru import logger
from logging_config import configure_logger

# Both used for BaseModel
from pydantic import BaseModel

from datetime import datetime
from kafka import KafkaProducer, producer
from kafka.errors import KafkaError

# GCP
from google.cloud import storage

# Configure logging
configure_logger()

# Create class (schema) for the JSON
# Date get's ingested as string and then before writing validated
class InvoiceItem(BaseModel):
    InvoiceNo: int
    StockCode: str
    Description: str
    Quantity: int
    InvoiceDate: str
    UnitPrice: float
    CustomerID: int
    Country: str

# This is important for general execution and the docker later
app = FastAPI()

# Base URL
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Add a new invoice
@app.post("/invoiceitem")
async def post_invoice_item(item: InvoiceItem):  # body awaits a JSON with invoice item information
    logger.info(f"Message received: {item}")
    try:
        # Evaluate the timestamp and parse it to a datetime object
        date = datetime.strptime(item.InvoiceDate, "%d/%m/%Y %H:%M")
        logger.debug(f"Found a timestamp: {date}")

        # Replace the original date with a new datetime format
        item.InvoiceDate = date.strftime("%d-%m-%Y %H:%M:%S")
        logger.debug(f"New item date: {item.InvoiceDate}")
        
        # Parse item back to JSON
        json_of_item = jsonable_encoder(item)
        
        # Dump the JSON out as a string
        json_as_string = json.dumps(json_of_item)
        logger.debug(f"JSON string of item: {json_as_string}")
        
        # Produce the string to Kafka
        produce_kafka_string(json_as_string)

        # Return the created item as JSON with a 201 status
        return JSONResponse(content=json_of_item, status_code=201)
    
    # Will be thrown by datetime if the date does not fit
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return JSONResponse(content=jsonable_encoder(item), status_code=400)
    
@app.post("/process-data-trigger-v2")
async def process_data_trigger(request: Request):
    """Handle Cloud Storage event trigger, process JSON data, and send to Kafka."""
    logger.info(f"Request received: {request}")

    try:
        # Parse the request body
        body = await request.json()
        logger.info(f"Parsed request body: {body}")
        
        bucket_name = body.get("bucket")
        file_name = body.get("name")
        
        # Log bucket and file name details
        logger.info(f"Bucket name: {bucket_name}, File name: {file_name}")

        # Ensure we're only processing the intended file
        if file_name != "Processed_Data.json":
            logger.info(f"Ignored file: {file_name}")
            return JSONResponse(content={"message": "Ignored non-target file."}, status_code=200)

        # Download and process the file from Cloud Storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        # Log before downloading the file content
        # logger.info(f"Downloading file: {file_name} from bucket: {bucket_name}")
        # json_data = json.loads(blob.download_as_text())
        # logger.info(f"Downloaded data: {json_data}")
        
        # Log before downloading the file content
        logger.info(f"Downloading file: {file_name} from bucket: {bucket_name}")
        file_content = blob.download_as_text()
        logger.info(f"Downloaded data: {file_content}")
        
        # Parse each JSON object separately
        json_data = [json.loads(line) for line in file_content.strip().splitlines()]
        logger.info(f"Parsed JSON data: {json_data}")

        # Process each invoice item in the JSON data
        for item_data in json_data:
            logger.debug(f"Processing item data: {item_data}")
            
            item = InvoiceItem(**item_data)
            
            # Format the date as required
            date = datetime.strptime(item.InvoiceDate, "%d/%m/%y %H:%M")  # Change %Y to %y
            item.InvoiceDate = date.strftime("%d-%m-%Y %H:%M:%S")  # Convert to four-digit year format if needed
            logger.debug(f"Formatted InvoiceDate: {item.InvoiceDate}")
            
            # Convert to JSON string
            json_as_string = json.dumps(jsonable_encoder(item))
            logger.debug(f"JSON string to be sent to Kafka: {json_as_string}")
            produce_kafka_string(json_as_string)

        logger.info("Processed and sent all items to Kafka.")
        return JSONResponse(content={"message": "Processed and sent to Kafka"}, status_code=201)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        

def produce_kafka_string(json_as_string):
    producer = None  # Initialize the producer to None
    
    try:
        logger.info("Attempting to create Kafka producer...")
        
        # Create Kafka producer
        producer = KafkaProducer(bootstrap_servers='kafka:9092', acks=1)
        logger.info("Kafka producer created successfully.")

        # Write the string as bytes because Kafka needs it this way
        future = producer.send('ingestion-topic', bytes(json_as_string, 'utf-8'))
        logger.info("Message sent to Kafka: %s", json_as_string)
        
        # Block until a single message is sent (or timeout)
        result = future.get(timeout=10)  # Wait for the send to complete

        logger.info("Produced message to Kafka topic 'ingestion-topic': %s", result)
    
    except KafkaError as e:
        logger.error("Failed to send message to Kafka: %s", e)
    except Exception as e:
        logger.error("An error occurred while producing Kafka message: %s", e)
    finally:
        if producer is not None:
            producer.close()  # Close the producer only if it was created
