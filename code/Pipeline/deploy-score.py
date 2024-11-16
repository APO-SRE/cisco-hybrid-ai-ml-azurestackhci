# Jeff Teeter, Ph.D.
# Cisco Systems, Inc.
import json
import sys
import time
import os
from datetime import datetime
import numpy as np
import pandas as pd
from random import randrange
import urllib
from urllib.parse import urlencode
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml import Input, Output
from azure.ai.ml.constants import InputOutputModes
from azure.ai.ml.entities import (
    BatchEndpoint,
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
    Model,
    Data,
    BatchRetrySettings,
    CodeConfiguration,
    Environment,
    BatchJob
)
from azure.ai.ml.constants import AssetTypes, BatchDeploymentOutputAction
# Load the configuration from the JSON file
with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)
# Assign the values to variables
subscription_id = config['subscription_id']
resource_group = config['resource_group']
workspace_name = config['workspace_name']
    
# Hard-code the configuration information
attach_name = "Cisco-k8s-dfault"  # Use the registered compute target name
managed_identity_client_id = "af6bcfce-fec2-4763-b40b-749f298b599b"  # Replace with the client ID of your managed identity
# Initialize ML client using DefaultAzureCredential with managed identity client ID
credential = DefaultAzureCredential(managed_identity_client_id=managed_identity_client_id)
ml_client = MLClient(
    credential=credential,
    subscription_id=subscription_id,
    resource_group_name=resource_group,
    workspace_name=workspace_name
)
# Retrieve the current workspace details
workspace = ml_client.workspaces.get(workspace_name)
print("Current workspace:", workspace.name)
# Make sure the compute cluster exists already
try:
    cpu_cluster = ml_client.compute.get(attach_name)
    print(f"You already have a cluster named {attach_name}, we'll reuse it as is.")
    print(f"Compute target '{attach_name}' status: {cpu_cluster.provisioning_state}")
except Exception as e:
    print(f"Error in attaching AKS-HCI compute: {e}")
    sys.exit(1)
# Ensure that there is an endpoint for batch scoring
endpoint_name = "machine-learning-cisco-ucs"
try:
    endpoint = ml_client.batch_endpoints.get(endpoint_name)
    print(f"You already have an endpoint named {endpoint_name}, we'll reuse it as is.")
except Exception as e:
    print(f"Creating a new batch endpoint... Error: {str(e)}")
    endpoint = BatchEndpoint(name=endpoint_name, description="Batch scoring endpoint for Chicago Parking Ticket payment status")
    try:
        ml_client.batch_endpoints.begin_create_or_update(endpoint).result()
        endpoint = ml_client.batch_endpoints.get(endpoint_name)
        print(f"Endpoint name:  {endpoint.name}")
    except Exception as create_error:
        print(f"Error creating endpoint: {str(create_error)}")
        raise
# Retrieve the parking tickets model
model = ml_client.models.get(name="Recievable-Predictor-Cisco-AKS-on-UCS-ML", version="1")
print("Retrieved model.")
# Get the correct environment
deployment_name = "UCS-batch-deployment"
# Function to wait for the endpoint to be in a 'Succeeded' state
def wait_for_endpoint(endpoint_name, timeout=1800, interval=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        endpoint = ml_client.batch_endpoints.get(endpoint_name)
        if endpoint.provisioning_state == "Succeeded":
            return True
        print(f"Waiting for endpoint {endpoint_name} to be in 'Succeeded' state...")
        time.sleep(interval)
    return False
# Wait for the endpoint to be in a 'Succeeded' state before proceeding
if not wait_for_endpoint(endpoint_name):
    print(f"Timeout waiting for endpoint {endpoint_name} to be in 'Succeeded' state.")
    sys.exit(1)
try:
    # Check if the deployment already exists
    deployment = ml_client.batch_deployments.get(name=deployment_name, endpoint_name=endpoint_name)
    print(f"Deployment named {deployment_name} already exists, reusing it.")
except Exception as e:
    print(f"No deployment exists--creating a new deployment... Error: {str(e)}")
    
    # Retrieve the environment
    try:
        environment = ml_client.environments.get(name="cisco-mlflow-azureml-env", version="1")
        print("Retrieved environment.")
    except Exception as env_error:
        print(f"Error retrieving environment: {str(env_error)}")
        raise
    
    # Create the deployment
    # For MLflow model deployment, the resource request requires at least 2 CPU cores and 4 GB of memory. 
    # Otherwise, the deployment will fail.
    try:
        deployment = ModelBatchDeployment(
            name=deployment_name,
            description="Batch scoring of payment status",
            endpoint_name=endpoint.name,
            model=model,
            environment=environment,
            code_configuration=CodeConfiguration(code="scripts", scoring_script="score_model.py"),
            compute=attach_name,
            settings=ModelBatchDeploymentSettings(
                instance_count=2,
                max_concurrency_per_instance=2,
                mini_batch_size=10,
                output_action=BatchDeploymentOutputAction.APPEND_ROW,
                output_file_name="predictions.csv",
                retry_settings=BatchRetrySettings(max_retries=3, timeout=300),
                logging_level="info",
                instance_type="standardinstancetype" # Specify the instance type
            )
        )
        
        print("Creating the deployment...")
        ml_client.batch_deployments.begin_create_or_update(deployment).result()
        print(f"Deployment {deployment_name} created successfully.")
    except Exception as dep_error:
        print(f"Error creating deployment: {str(dep_error)}")
        raise
    # Make the new deployment the default for the endpoint
    try:
        endpoint.defaults.deployment_name = deployment.name
        ml_client.batch_endpoints.begin_create_or_update(endpoint).result()
        print(f"Made deployment {deployment_name} the default for the endpoint {endpoint.name}.")
    except Exception as update_error:
        print(f"Error updating endpoint with default deployment: {str(update_error)}")
        raise
# Prepare the dataset
data_path = "data"
dataset_name = "ChicagoParkingTicketsUnlabeled"
try:
    chicago_dataset_unlabeled = ml_client.data.get(dataset_name, label="latest")
    print("Dataset already exists.")
except Exception as e:
    print(f"No dataset exists--creating a new dataset... Error: {str(e)}")
    chicago_dataset_unlabeled = Data(
        path=data_path,
        type=AssetTypes.URI_FOLDER,
        description="An unlabeled dataset for Chicago parking ticket payment status",
        name=dataset_name
    )
    ml_client.data.create_or_update(chicago_dataset_unlabeled)
    chicago_dataset_unlabeled = ml_client.data.get(dataset_name, label="latest")
    print("Dataset now exists.")
# NOTE: If you are getting a "BY_POLICY" error, make sure that your account is an Owner
# on the Azure ML workspace.  You must *explicitly* grant rights, even if you are the 
# subscription owner!
# Create a job to score the data
try:
    # Start batch scoring job
    job = ml_client.batch_endpoints.invoke(endpoint_name=endpoint.name, input=Input(type=AssetTypes.URI_FOLDER, path=chicago_dataset_unlabeled.path))
    print(f"Job {job.name} started successfully.")
    
    # Stream logs for job
    ml_client.jobs.stream(job.name)
    
    # Alternatively, you can periodically check the job status
    job_status = ml_client.jobs.get(job.name)
    while job_status.status not in ["Completed", "Failed"]:
        print(f"Job {job.name} is in state: {job_status.status}...")
        time.sleep(30)
        job_status = ml_client.jobs.get(job.name)
    if job_status.status == "Completed":
        print("Job completed successfully.")
        # Download job output if needed
        ml_client.jobs.download(name=job.name, output_name='score', download_path='./')
    else:
        print("Job failed. Please check the job logs for errors.")
except Exception as job_error:
    print(f"Error during batch scoring job: {str(job_error)}")
    raise