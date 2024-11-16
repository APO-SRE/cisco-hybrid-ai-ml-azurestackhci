# Jeff Teeter, Ph.D.
# Cisco Systems, Inc.

import json
import sys
import os
from datetime import datetime
import numpy as np
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, load_component, Input, Output
from azure.ai.ml.dsl import pipeline

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

# Set up the KubernetesCompute for the Arc-enabled AKS-HCI cluster
try:
    arcK_compute = ml_client.compute.get(attach_name)
    print(f"Compute target '{attach_name}' attached successfully.")
except Exception as e:
    print(f"Error in attaching AKS-HCI compute: {e}")
    sys.exit(1)

# Load pipeline components
parent_dir = "./config"
replace_missing_values = load_component(source=os.path.join(parent_dir, "feature-replace-missing-values.yml"))
feature_engineering = load_component(source=os.path.join(parent_dir, "feature-engineering.yml"))
feature_selection = load_component(source=os.path.join(parent_dir, "feature-selection.yml"))
split_data = load_component(source=os.path.join(parent_dir, "split-data.yml"))
train_model = load_component(source=os.path.join(parent_dir, "train-model.yml"))
register_model = load_component(source=os.path.join(parent_dir, "register-model.yml"))

@pipeline(name="UCS_training_pipeline", description="Build a UCS training pipeline")
def build_pipeline(raw_data):
    step_replace_missing_values = replace_missing_values(input_data=raw_data)
    step_feature_engineering = feature_engineering(input_data=step_replace_missing_values.outputs.output_data)
    step_feature_selection = feature_selection(input_data=step_feature_engineering.outputs.output_data)
    step_split_data = split_data(input_data=step_feature_selection.outputs.output_data)

    train_model_data = train_model(
        train_data=step_split_data.outputs.output_data_train,
        test_data=step_split_data.outputs.output_data_test,
        max_leaf_nodes=128,
        min_samples_leaf=32,
        max_depth=12,
        learning_rate=0.1,
        n_estimators=100
    )
    register_model(model=train_model_data.outputs.model_output, test_report=train_model_data.outputs.test_report)
    return {"model": train_model_data.outputs.model_output, "report": train_model_data.outputs.test_report}

def prepare_pipeline_job(compute_target_name):
    # Load dataset
    cpt_asset = ml_client.data.get(name="ChicagoParkingTickets", version="1")
    raw_data = Input(type='uri_folder', path=cpt_asset.path)
    
    pipeline_job = build_pipeline(raw_data)
    # Set the KubernetesCompute target for the pipeline
    pipeline_job.settings.default_compute = compute_target_name
    pipeline_job.settings.default_datastore = "workspaceblobstore"
    pipeline_job.settings.force_rerun = True
    pipeline_job.display_name = f"UCS_train_pipeline_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    pipeline_job.settings.node_selector = {"nodepool": "largepool"}  # Ensure the correct node pool is selected
    pipeline_job.environment = "cisco-mlflow-azureml-env:1"  # Specify the environment version here
    return pipeline_job

# Prepare and submit the pipeline job
prepped_job = prepare_pipeline_job(arcK_compute.name)
print(f"Submitting pipeline job with environment: {prepped_job.environment}")
print(f"Using compute target: {arcK_compute.name}")
ml_client.jobs.create_or_update(prepped_job, experiment_name="machine-learning-cisco-ucs")

print("Now look in the Azure ML Jobs UI to see the status of the pipeline job in the 'machine-learning-cisco-ucs' experiment.")