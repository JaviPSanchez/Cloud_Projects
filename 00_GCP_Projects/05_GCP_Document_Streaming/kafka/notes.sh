# Select project
gcloud config set project gcp-classification-v1
# Get a subnet identifier
gcloud compute networks subnets describe default --region=us-central1 \
    --format='value(selfLink)' | sed 's|.*/compute/v1/||'
# Output
projects/PROJECT_ID/regions/REGION/subnetworks/SUBNET_ID
projects/gcp-classification-v1/regions/us-central1/subnetworks/default

# Export variables
export PROJECT_ID=gcp-classification-v1
export SUBNET_ID=projects/$PROJECT_ID/regions/us-central1/subnetworks/default


# Print all variables
printenv
# check specific variables
echo $PROJECT_ID
echo $SUBNET_ID

# Create a cluster
gcloud beta managed-kafka clusters create test-cluster \
    --location=us-central1 \
    --cpu=3 \
    --memory=3GiB \
    --subnets=$SUBNET_ID \
    --async

# Output:
Create request issued for: [test-cluster]
Check operation [projects/gcp-classification-v1/locations/us-central1/operations/operation-1730362546926-625c16cf1342f-4429fdfa-8334adae] for status.

# Store the operatio_id
export OPERATION_ID=operation-1730362546926-625c16cf1342f-4429fdfa-8334adae

# One cluster created, check details
gcloud beta managed-kafka clusters describe kafka-cluster \
    --location=us-central1

# Output:
bootstrapAddress: bootstrap.kafka-cluster.us-central1.managedkafka.gcp-classification-v1.cloud.goog
capacityConfig:
  memoryBytes: '12884901888'
  vcpuCount: '3'
createTime: '2024-10-30T08:50:33.529766391Z'
gcpConfig:
  accessConfig:
    networkConfigs:
    - subnet: projects/gcp-classification-v1/regions/us-central1/subnetworks/default
name: projects/gcp-classification-v1/locations/us-central1/clusters/kafka-cluster
rebalanceConfig:
  mode: AUTO_REBALANCE_ON_SCALE_UP
state: ACTIVE
updateTime: '2024-10-30T09:19:38.788919440Z'

# Retrive bootstrp address
gcloud beta managed-kafka clusters describe kafka-cluster \
    --location=us-central1 \
    --format="value(bootstrapAddress)"

# Output:
bootstrap.kafka-cluster.us-central1.managedkafka.gcp-classification-v1.cloud.goog

# Create a topic
gcloud beta managed-kafka topics create t1 \
    --cluster=kafka-cluster --location=us-central1 --partitions=10 \
    --replication-factor=3

# Descrive a topic
gcloud beta managed-kafka topics describe t1 \
    --cluster=kafka-cluster --location=us-central1

# Output
name: projects/gcp-classification-v1/locations/us-central1/clusters/kafka-cluster/topics/t1
partitionCount: 10
replicationFactor: 3

# Set Up Client Machine

gcloud compute instances create kafka-instance \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --subnet=$SUBNET_ID \
    --zone=us-central1-f

# output
NAME: kafka-instance
ZONE: us-central1-f
MACHINE_TYPE: n1-standard-1
PREEMPTIBLE:
INTERNAL_IP: 10.128.0.10
EXTERNAL_IP: 23.236.52.223
STATUS: RUNNING

# Give the Compute Engine default service account the permissions to use Managed Service for Apache Kafka

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role=roles/managedkafka.client

# Project number we can check in IAM > Service account
1058872974041-compute@developer.gserviceaccount.com

export PROJECT_NUMBER=1058872974041

# Access VM:

ssh kafka-cluster