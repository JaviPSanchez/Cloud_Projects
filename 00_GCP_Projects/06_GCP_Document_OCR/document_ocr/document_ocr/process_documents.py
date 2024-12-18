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
PROCESSOR_DISPLAY_NAME=os.getenv("PROCESSOR_DISPLAY_NAME")


def quickstart(
    project_id: str,
    location: str,
    file_path: str,
    processor_display_name: str,
):
    logger.info("Starting Document AI quickstart function")
    logger.debug(f"Parameters - Project ID: {project_id}, Location: {location}, File Path: {file_path}, Processor Display Name: {processor_display_name}")

    # Setting API endpoint based on location
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    logger.info(f"Client options set with endpoint {opts.api_endpoint}")

    try:
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        logger.info("DocumentProcessorServiceClient initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize DocumentProcessorServiceClient: {e}")
        return

    parent = client.common_location_path(project_id, location)
    logger.debug(f"Parent location path set to {parent}")

    try:
        # Create a Processor
        processor = client.create_processor(
            parent=parent,
            processor=documentai.Processor(
                type_="OCR_PROCESSOR",  # Specify the processor type
                display_name=processor_display_name,
            ),
        )
        logger.info(f"Processor created with display name {processor_display_name}")
        logger.debug(f"Processor Name: {processor.name}")
    except Exception as e:
        logger.error(f"Failed to create processor: {e}")
        return

    # Reading the file into memory
    try:
        with open(file_path, "rb") as image:
            image_content = image.read()
            logger.info(f"File '{file_path}' read successfully")
    except Exception as e:
        logger.error(f"Failed to read file '{file_path}': {e}")
        return

    raw_document = documentai.RawDocument(
        content=image_content,
        mime_type="application/pdf",
    )
    logger.debug("Raw document prepared with content from file")

    # Configuring the process request
    request = documentai.ProcessRequest(name=processor.name, raw_document=raw_document)
    logger.info("Process request configured")

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


quickstart(PROJECT_ID, LOCATION, FILE_PATH, PROCESSOR_DISPLAY_NAME)
