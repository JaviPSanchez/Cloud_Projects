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
INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME")
OUTPUT_BUCKET_NAME = os.getenv("OUTPUT_BUCKET_NAME")
logger.debug("Done loading environment variables!")

# Raise an error if critical environment variables are missing
if not INPUT_BUCKET_NAME or not OUTPUT_BUCKET_NAME:
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

def upload_json_to_output_bucket(df_json):
    """Upload the JSON content to the output bucket."""
    client = storage.Client()
    output_bucket = client.bucket(OUTPUT_BUCKET_NAME)

    # Prepare JSON data as a single text string
    json_data = "\n".join(df_json)  # Each line represents a JSON object

    # Define blob (file) name for the new object in the output bucket
    output_blob = output_bucket.blob("Processed_Data.json")

    # Upload JSON data to the blob
    output_blob.upload_from_string(json_data, content_type="application/json")
    logger.info(f"Uploaded JSON data to {OUTPUT_BUCKET_NAME}/Processed_Data.json")

@functions_framework.cloud_event
def handle_storage_event(cloud_event):
    """Triggered by a file upload to the input Cloud Storage bucket."""
    
    data = cloud_event.data
    file_name = data["name"]
    bucket_name = data["bucket"]

    logger.info(f"Cloud Storage event triggered by file: {file_name} in bucket: {bucket_name}")

    # Only process if the event bucket matches the input bucket
    if bucket_name == INPUT_BUCKET_NAME:
        client = storage.Client()
        input_bucket = client.bucket(INPUT_BUCKET_NAME)
        blob = input_bucket.blob(file_name)

        # Download the CSV file as text
        csv_data = blob.download_as_text()
        logger.info(f"Downloaded '{file_name}' from bucket '{bucket_name}'.")

        # Process CSV data to create JSON column
        df_json = process_csv_data(csv_data)
        logger.info(f"Processed data to JSON format.")

        # Upload JSON data to the output bucket
        upload_json_to_output_bucket(df_json)
        return "Processed and uploaded JSON successfully."
    else:
        logger.info(f"Ignored file: {file_name} (not in the target bucket).")
        return "Ignored non-target bucket."
