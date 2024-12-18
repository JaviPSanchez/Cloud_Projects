
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore

from dotenv import load_dotenv

load_dotenv("../secrets/.env")

PROJECT_ID=os.getenv("PROJECT_ID")
LOCATION=os.getenv("LOCATION")


def fetch_processor_types_sample(project_id: str, location: str) -> None:
    # You must set the api_endpoint if you use a location other than 'us'.
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the location
    # e.g.: projects/project_id/locations/location
    parent = client.common_location_path(project_id, location)

    # Fetch all processor types
    response = client.fetch_processor_types(parent=parent)

    print("Processor types:")
    # Print the available processor types
    for processor_type in response.processor_types:
        if processor_type.allow_creation:
            print(processor_type.type_)

fetch_processor_types_sample(PROJECT_ID, LOCATION)
