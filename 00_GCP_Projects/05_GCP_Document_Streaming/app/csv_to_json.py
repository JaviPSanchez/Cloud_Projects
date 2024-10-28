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
BUCKET_NAME = os.getenv("RAW_BUCKET_NAME")
logger.debug("Done loading environment variables!")

# Only for Local Development Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(google_credentials_path)

# Raise an error if critical environment variables are missing
if not BUCKET_NAME:
    logger.critical("Critical environment variables are missing! Exiting program.")
    raise EnvironmentError("Environment variables must be set.")


def read_csv_from_storage():
    """Read the 'Online_Small_Retail.csv' file from GCP Storage."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob("Online_Small_Retail.csv")

    logger.info("Attempting to download 'Online_Small_Retail.csv' from storage bucket.")
    
    # Download the file as string data
    csv_data = blob.download_as_text()
    
    # Print or process the CSV data as needed
    logger.info("Successfully downloaded 'Online_Small_Retail.csv'")
    print(csv_data)  # or return csv_data to process further

    return csv_data

# Run the function if in a local testing environment
if __name__ == "__main__":
    csv_content = read_csv_from_storage()