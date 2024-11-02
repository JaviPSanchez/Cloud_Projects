from typing import List

from google.cloud import managedkafka_v1


def list_clusters(
    project_id: str,
    region: str,
) -> List[str]:
    """
    List Kafka clusters in a given project ID and region.

    Args:
        project_id: Google Cloud project ID.
        region: Cloud region.
    """

    client = managedkafka_v1.ManagedKafkaClient()

    request = managedkafka_v1.ListClustersRequest(
        parent=client.common_location_path(project_id, region),
    )

    response = client.list_clusters(request=request)
    for cluster in response:
        print("Got cluster:", cluster)

    return [cluster.name for cluster in response]

list_clusters("gcp-classification-v1", "us-central1")
