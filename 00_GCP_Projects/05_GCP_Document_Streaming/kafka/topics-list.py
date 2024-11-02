import os
import json
import io
from pathlib import Path
from loguru import logger
from logging_config import configure_logger
from typing import List

from google.cloud import managedkafka_v1

# Configure logging
configure_logger()

# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))
print(BASEDIR)

# Define path to the credentials file and set GOOGLE_APPLICATION_CREDENTIALS
# google_credentials_path = os.path.join(BASEDIR, '../secrets/key_access_sql.json')
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path


def list_topics(
    project_id: str,
    region: str,
    cluster_id: str,
) -> List[str]:
    """
    List Kafka topics in a cluster.

    Args:
        project_id: Google Cloud project ID.
        region: Cloud region.
        cluster_id: ID of the Kafka cluster.
    """

    client = managedkafka_v1.ManagedKafkaClient()

    request = managedkafka_v1.ListTopicsRequest(
        parent=client.cluster_path(project_id, region, cluster_id),
    )

    response = client.list_topics(request=request)
    for topic in response:
        print("Got topic:", topic)

    return [topic.name for topic in response]

list_topics("gcp-classification-v1", "us-central1", "kafka-cluster")