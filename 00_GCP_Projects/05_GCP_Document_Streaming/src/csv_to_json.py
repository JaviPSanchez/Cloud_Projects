import os
import json
import io
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from google.cloud import storage
import functions_framework
from loguru import logger
from logging_config import configure_logger

# Configure logging
configure_logger()

# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))
print(BASEDIR)

# Load the .env file
load_dotenv(os.path.join(BASEDIR, '../secrets/.env'))

# Define path to the credentials file and set GOOGLE_APPLICATION_CREDENTIALS
google_credentials_path = os.path.join(BASEDIR, '../secrets/key_access_sql.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path

# Environment variables
logger.debug("Attempting to load environment variables!")
BUCKET_NAME = os.getenv("BUCKET_NAME")
JSON_OBJECT_NAME = os.getenv("JSON_OBJECT_NAME", "Online_Small_Retail.json")
logger.debug("Done loading environment variables!")

# Raise an error if critical environment variables are missing
if not BUCKET_NAME or not JSON_OBJECT_NAME:
    logger.critical("Critical environment variables are missing! Exiting program.")
    raise EnvironmentError("Environment variables must be set.")

def process_csv_data(csv_data):
    """Process the CSV data and return it as a JSON column."""
    # Load CSV data into a DataFrame
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Add a JSON column where each row in the column is a JSON representation of that row
    df['json'] = df.to_json(orient='records', lines=True).splitlines()
    
    # Extract only the JSON column
    df_json = df['json']
    return df_json

def upload_json_to_storage(df_json):
    """Upload the JSON content as a new object in the same bucket."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # Prepare JSON data as a single text string
    json_data = "\n".join(df_json)  # Each line represents a JSON object

    # Define blob (file) name for the new object in the existing bucket
    blob = bucket.blob(JSON_OBJECT_NAME)

    # Upload JSON data to the blob
    blob.upload_from_string(json_data, content_type="application/json")
    logger.info(f"Uploaded JSON data to {BUCKET_NAME}/{JSON_OBJECT_NAME}")

@functions_framework.cloud_event
def handle_storage_event(cloud_event):
    """Triggered by a file upload to Cloud Storage."""
    
    data = cloud_event.data
    file_name = data["name"]
    bucket_name = data["bucket"]

    logger.info(f"Cloud Storage event triggered by file: {file_name} in bucket: {bucket_name}")

    # Only process if the event bucket and filename match expectations
    if bucket_name == BUCKET_NAME and file_name == "Online_Small_Retail.csv":
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_name)

        # Download the CSV file as text
        csv_data = blob.download_as_text()
        logger.info(f"Downloaded '{file_name}' from bucket '{bucket_name}'.")

        # Process CSV data to create JSON column
        df_json = process_csv_data(csv_data)
        logger.info(f"df_json: {df_json}")

        # Upload JSON data as a new object in the same bucket
        upload_json_to_storage(df_json)
        return "Processed and uploaded JSON successfully."
    else:
        logger.info(f"Ignored file: {file_name} (not the target CSV file).")
        return "Ignored non-target file."
