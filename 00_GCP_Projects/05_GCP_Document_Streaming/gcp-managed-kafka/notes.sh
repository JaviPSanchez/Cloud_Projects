# Select project
gcloud projects list
gcloud config set project gcp-classification-v1
# Show VM
gcloud compute instances list


# Get a subnet identifier
gcloud compute networks subnets describe default --region=us-central1 \
    --format='value(selfLink)' | sed 's|.*/compute/v1/||'
# Output
projects/PROJECT_ID/regions/REGION/subnetworks/SUBNET_ID
projects/gcp-classification-v1/regions/us-central1/subnetworks/default

# Export variables
export PROJECT_ID=gcp-classification-v1
export SUBNET_ID=projects/$PROJECT_ID/regions/us-central1/subnetworks/default


# gcloud compute ssh — project gcp-classification-v1 — zone=us-central1" \
# -r kafka-cluster --dns 10.128.0.10/16


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

# Access VM, update nano ~./.ssh/config 

# Google Cloud Platform
Host gcp-kafka
  HostName 23.236.52.223
  User weather-vm
  IdentityFile ~/.ssh/gcp
  IdentitiesOnly yes

ssh gcp-kafka

# Check version and update:
hostnamectl
# if debian
sudo apt update
sudo apt upgrade

# Install Java to run Kafka command line tools and wget to help download dependencies
sudo apt-get install default-jre wget

# Install the Kafka command line tools on the VM.
wget -O kafka_2.13-3.6.2.tgz  https://downloads.apache.org/kafka/3.6.2/kafka_2.13-3.6.2.tgz
tar xfz kafka_2.13-3.6.2.tgz
export KAFKA_HOME=$(pwd)/kafka_2.13-3.6.2
export PATH=$PATH:$KAFKA_HOME/bin

# This code downloads and extracts the Apache Kafka distribution and sets the
# KAFKA_HOME environment variable for convenience, and adds the Kafka bin
# directory to the PATH variable.

# Set up the Managed Service for Apache Kafka authentication library.


# Download the dependencies and install them locally. Since the Kafka command line tools look
# for Java dependencies in the lib directory of the Kafka installation directory, we add these
# dependencies there.

wget https://github.com/googleapis/managedkafka/releases/download/v1.0.1/release-and-dependencies.zip
sudo apt-get install unzip
unzip -n release-and-dependencies.zip -d $KAFKA_HOME/libs/

# Set up the client machine configuration properties.


# This code configures a Kafka client for the following settings:
# Use SASL_SSL for secure communication with the Kafka cluster.
# Employ OAuth 2.0 bearer tokens for authentication.
# Use a Google Cloud-specific login callback handler to obtain OAuth 2.0 tokens.

cat <<EOF >> client.properties
security.protocol=SASL_SSL
sasl.mechanism=OAUTHBEARER
sasl.login.callback.handler.class=com.google.cloud.hosted.kafka.auth.GcpLoginCallbackHandler
sasl.jaas.config=org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required;
EOF

# Use Kafka command line tools

# Run these commands on the client machine.

export PROJECT_ID=gcp-classification-v1

# Set up the BOOTSTRAP address as an environment variable. This can be fetched from describing the cluster that was created.

export BOOTSTRAP=bootstrap.kafka-cluster.us-central1.managedkafka.$PROJECT_ID.cloud.goog:9092

# List the topics in the cluster.
kafka-topics.sh --list \
--bootstrap-server $BOOTSTRAP \
--command-config client.properties

# Write a message to the topic t1 and consume it.

echo "hello world" | kafka-console-producer.sh --topic t1 \
--bootstrap-server $BOOTSTRAP --producer.config client.properties

echo "hello world" | kafka-console-producer.sh --topic t2 \
--bootstrap-server $BOOTSTRAP --producer.config client.properties

# Consume the message from topic t1.

kafka-console-consumer.sh --topic t1 --from-beginning \
 --bootstrap-server $BOOTSTRAP --consumer.config client.properties

kafka-console-consumer.sh --topic t2 --from-beginning \
 --bootstrap-server $BOOTSTRAP --consumer.config client.properties

# Run a simpler producer performance test.

kafka-producer-perf-test.sh --topic t1 --num-records 1000000 \
--throughput -1 --print-metrics --record-size 1024 \
--producer-props bootstrap.servers=$BOOTSTRAP --producer.config client.properties

# If desired, clean up and delete project
gcloud beta managed-kafka clusters delete kafka-cluster --location=us-central1


