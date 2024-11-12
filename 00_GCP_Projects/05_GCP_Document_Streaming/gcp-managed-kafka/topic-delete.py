from pathlib import Path
from dotenv import load_dotenv
import os
from loguru import logger
from logging_config import configure_logger

from google.api_core.exceptions import NotFound
from google.cloud import managedkafka_v1


# Configure logging
configure_logger()


# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__)) # folder kafka

# Load the .env file
load_dotenv(os.path.join(BASEDIR, '.env'))

# Environment variables
logger.debug("Attempting to load environment variables!")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
CLUSTER_ID = os.getenv("CLUSTER_ID")
logger.debug("Done loading environment variables!")





def delete_topic(
    project_id: str,
    region: str,
    cluster_id: str,
    topic_id: str,
) -> None:
    """
    Delete a Kafka topic.

    Args:
        project_id: Google Cloud project ID.
        region: Cloud region.
        cluster_id: ID of the Kafka cluster.
        topic_id: ID of the Kafka topic.

    Raises:
        This method will raise the exception if the topic is not found.
    """

    client = managedkafka_v1.ManagedKafkaClient()

    topic_path = client.topic_path(project_id, region, cluster_id, topic_id)
    request = managedkafka_v1.DeleteTopicRequest(name=topic_path)

    try:
        client.delete_topic(request=request)
        print("Deleted topic")
    except NotFound:
        print(f"Topic {topic_path} not found")
        
        
delete_topic(PROJECT_ID, REGION, CLUSTER_ID, "t1")
