import os
from typing import Optional
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
from dotenv import load_dotenv  # Environment variables
from loguru import logger
from helpers.logging_config import configure_logger

# Load environment variables
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '../secrets/.env'))

# Configure logging
configure_logger()

# Environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
PROCESSOR_ID = os.getenv("PROCESSOR_ID")
FILE_PATH = os.getenv("FILE_PATH")
MIME_TYPE = os.getenv("MIME_TYPE")
FIELD_MASK = os.getenv("FIELD_MASK")
PROCESSOR_VERSION_ID = os.getenv("PROCESSOR_VERSION_ID")

# Define output directories
OK_DIR = 'OK'
KO_DIR = 'KO'
os.makedirs(OK_DIR, exist_ok=True)
os.makedirs(KO_DIR, exist_ok=True)

def get_timestamp():
    """
    Generates a timestamp in the format YYMMDD_HHMM.
    
    Returns:
        str: The formatted timestamp.
    """
    from datetime import datetime
    return datetime.now().strftime('%y%m%d_%H%M')

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

    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    logger.info(f"Client options set with endpoint {opts.api_endpoint}")

    try:
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        logger.info("DocumentProcessorServiceClient initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize DocumentProcessorServiceClient: {e}")
        return

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

    try:
        with open(file_path, "rb") as image:
            image_content = image.read()
            logger.info(f"File '{file_path}' read successfully")
    except Exception as e:
        logger.error(f"Failed to read file '{file_path}': {e}")
        return

    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
    logger.debug("Raw document prepared with binary data from file")
    
    total_pages = 10  # Replace with actual page count logic if needed
    process_options = documentai.ProcessOptions(
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(pages=list(range(1, total_pages + 1)))
    )
    logger.debug("Process options configured for specific pages")

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
        # Save to KO folder with error message
        ko_filename = os.path.join(KO_DIR, f'KO_{get_timestamp()}_{os.path.basename(file_path).replace(".pdf", "")}.txt')
        with open(ko_filename, 'w') as ko_file:
            ko_file.write(f'Error: {str(e)}\n')
        return

    document = result.document
    logger.info("Retrieved processed document")

    if document.text.strip():  # Only save if there is text
        logger.info("The document contains the following text:")
        logger.info(document.text)
        
        # Save to OK folder
        ok_filename = os.path.join(OK_DIR, f'OK_{get_timestamp()}_{os.path.basename(file_path).replace(".pdf", "")}.txt')
        with open(ok_filename, 'w', encoding='utf8') as ok_file:
            ok_file.write(document.text)
            logger.info(f"Text successfully written to {ok_filename}")
    else:
        logger.warning("No text found in the processed document.")
        # Save to KO folder with no text found
        ko_filename = os.path.join(KO_DIR, f'KO_{get_timestamp()}_{os.path.basename(file_path).replace(".pdf", "")}.txt')
        with open(ko_filename, 'w') as ko_file:
            ko_file.write('No text extracted\n')

process_document_sample(PROJECT_ID, LOCATION, PROCESSOR_ID, FILE_PATH, MIME_TYPE, FIELD_MASK, PROCESSOR_VERSION_ID)
