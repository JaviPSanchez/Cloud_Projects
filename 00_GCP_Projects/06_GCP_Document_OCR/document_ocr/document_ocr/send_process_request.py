import os
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore

# Logs
from loguru import logger
from helpers.logging_config import configure_logger

from dotenv import load_dotenv

load_dotenv("../secrets/.env")

configure_logger()


PROJECT_ID=os.getenv("PROJECT_ID")
LOCATION=os.getenv("LOCATION")
PROCESSOR_ID=os.getenv("PROCESSOR_ID")
FILE_PATH=os.getenv("FILE_PATH")
MIME_TYPE=os.getenv("MIME_TYPE")
FIELD_MASK=os.getenv("FIELD_MASK")
PROCESSOR_VERSION_ID=os.getenv("PROCESSOR_VERSION_ID")


def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    field_mask: Optional[str] = None,
    processor_version_id: Optional[str] = None,
) -> None:
    logger.info("Starting document processing sample")
    logger.debug(f"Parameters - Project ID: {project_id}, Location: {location}, Processor ID: {processor_id}, File Path: {file_path}, Mime Type: {mime_type}, Field Mask: {field_mask}, Processor Version ID: {processor_version_id}")

    # Setting API endpoint based on location
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    logger.info(f"Client options set with endpoint {opts.api_endpoint}")

    try:
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        logger.info("DocumentProcessorServiceClient initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize DocumentProcessorServiceClient: {e}")
        return

    # Determine resource path based on processor version
    try:
        if processor_version_id:
            name = client.processor_version_path(project_id, location, processor_id, processor_version_id)
            logger.debug(f"Processor version path set to {name}")
        else:
            name = client.processor_path(project_id, location, processor_id)
            logger.debug(f"Processor path set to {name}")
    except Exception as e:
        logger.error(f"Failed to construct processor path: {e}")
        return

    # Reading the file into memory
    try:
        with open(file_path, "rb") as image:
            image_content = image.read()
            logger.info(f"File '{file_path}' read successfully")
    except Exception as e:
        logger.error(f"Failed to read file '{file_path}': {e}")
        return

    # Load binary data
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
    logger.debug("Raw document prepared with binary data from file")

    # Setting up process options
    process_options = documentai.ProcessOptions(
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(pages=[1])
    )
    logger.debug("Process options configured for specific pages")

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
        process_options=process_options,
    )
    logger.info("Process request configured successfully")

    try:
        result = client.process_document(request=request)
        logger.info("Document processed successfully")
    except Exception as e:
        logger.error(f"Failed to process document: {e}")
        return

    document = result.document
    logger.info("Retrieved processed document")

    logger.info("The document contains the following text:")
    logger.info(document.text)


process_document_sample(PROJECT_ID, LOCATION, PROCESSOR_ID, FILE_PATH, MIME_TYPE, FIELD_MASK, PROCESSOR_VERSION_ID)
