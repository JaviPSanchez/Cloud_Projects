from google.cloud import managedkafka_v1


def get_cluster(
    project_id: str,
    region: str,
    cluster_id: str,
) -> managedkafka_v1.Cluster:
    """
    Get a Kafka cluster.

    Args:
        project_id: Google Cloud project ID.
        region: Cloud region.
        cluster_id: ID of the Kafka cluster.
    """

    client = managedkafka_v1.ManagedKafkaClient()

    cluster_path = client.cluster_path(project_id, region, cluster_id)
    request = managedkafka_v1.GetClusterRequest(
        name=cluster_path,
    )

    cluster = client.get_cluster(request=request)
    print("Got cluster:", cluster)

    return cluster

get_cluster("gcp-classification-v1", "us-central1", "kafka-cluster")
