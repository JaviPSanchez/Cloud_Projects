# Libraries
import os
import base64
import json
import zipfile
import io
from pathlib import Path
from dotenv import load_dotenv
# GCP
from google.cloud import storage
import functions_framework
# Custom Logging
from loguru import logger
from logging_config import configure_logger

# Configure logging
configure_logger()

# Local Development
dotenv_path = Path("../secrets/.env")
google_credentials_path = Path("../secrets/key_access_sql.json")
load_dotenv(dotenv_path)


# Environment variables
logger.debug("Attempting to load environment variables!")
RAW_BUCKET_NAME = os.getenv("RAW_BUCKET_NAME")
UNZIP_BUCKET_NAME = os.getenv("UNZIP_BUCKET_NAME")
logger.debug("Done loading environment variables!")

# Only for Local Development Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(google_credentials_path)

# Raise an error if critical environment variables are missing
if not RAW_BUCKET_NAME or not UNZIP_BUCKET_NAME:
    logger.critical("Critical environment variables are missing! Exiting program.")
    raise EnvironmentError("Environment variables must be set.")

def unzip_and_upload(raw_bucket_name, zip_blob_name, unzip_bucket_name):
    """Unzips files from a zip archive stored in Cloud Storage and uploads them to a different bucket."""
    storage_client = storage.Client()
    raw_bucket = storage_client.bucket(raw_bucket_name)
    unzip_bucket = storage_client.bucket(unzip_bucket_name)
    zip_blob = raw_bucket.blob(zip_blob_name)

    # Download the zip file in-memory
    zip_data = io.BytesIO(zip_blob.download_as_bytes())

    try:
        # Extract the files from the zip archive
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                # Read each file in the archive
                file_data = zip_ref.read(file_name)
                
                # Create a blob for each unzipped file and upload to the unzip bucket
                destination_blob = unzip_bucket.blob(file_name)
                destination_blob.upload_from_string(file_data)
                
                logger.info(f"Extracted and uploaded {file_name} to {unzip_bucket_name}.")
    except Exception as e:
        logger.exception(f"Error during unzip_and_upload: {e}")
        

# Triggered from a message on a Cloud Pub/Sub topic
@functions_framework.cloud_event
def listen_from_storage(cloud_event):
    """Triggered by an event from Cloud Storage when a file is uploaded to the raw data bucket."""
    logger.info("Cloud event triggered")
    logger.info(f"Cloud Event: {cloud_event}")

    # Parse the Cloud Event to get file information
    data = cloud_event.data
    file_name = data["name"]
    bucket_name = data["bucket"]

    if bucket_name == RAW_BUCKET_NAME and file_name.endswith(".zip"):
        logger.info(f"Detected new zip file: {file_name}")
        unzip_and_upload(raw_bucket_name=RAW_BUCKET_NAME, zip_blob_name=file_name, unzip_bucket_name=UNZIP_BUCKET_NAME)
        return "Success"
    else:
        logger.info(f"Ignored file: {file_name} (not a zip file in the raw data bucket)")
        return "Ignored"
