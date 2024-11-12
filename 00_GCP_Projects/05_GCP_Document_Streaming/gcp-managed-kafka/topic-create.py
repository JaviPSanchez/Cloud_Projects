from pathlib import Path
from dotenv import load_dotenv
import os
from loguru import logger
from logging_config import configure_logger

from google.api_core.exceptions import AlreadyExists
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
TOPIC_ID = os.getenv("TOPIC_ID")
logger.debug("Done loading environment variables!")


def create_topic(
    project_id: str,
    region: str,
    cluster_id: str,
    topic_id: str,
    partition_count: int,
    replication_factor: int,
    configs: dict[str, str],
) -> None:
    """
    Create a Kafka topic.

    Args:
        project_id: Google Cloud project ID.
        region: Cloud region.
        cluster_id: ID of the Kafka cluster.
        topic_id: ID of the Kafka topic.
        partition_count: Number of partitions in a topic..
        replication_factor: Number of replicas of each partition.
        configs: Configuration of the topic. For a list of configs, one can check https://kafka.apache.org/documentation/#topicconfigs.

    Raises:
        This method will raise the exception if the topic already exists.
    """

    client = managedkafka_v1.ManagedKafkaClient()

    topic = managedkafka_v1.Topic()
    topic.name = client.topic_path(project_id, region, cluster_id, topic_id)
    topic.partition_count = partition_count
    topic.replication_factor = replication_factor
    topic.configs = configs

    request = managedkafka_v1.CreateTopicRequest(
        parent=client.cluster_path(project_id, region, cluster_id),
        topic_id=topic_id,
        topic=topic,
    )

    try:
        response = client.create_topic(request=request)
        print("Created topic:", response.name)
    except AlreadyExists:
        print(f"{topic.name} already exists")
          
# Call the function with a properly formatted dictionary:
create_topic(
    PROJECT_ID,
    REGION,
    CLUSTER_ID,
    "t2",
    10,
    3,
    {"max.message.bytes": "64000", "flush.messages": "1"}  # Dictionary with proper key-value pairs
)
