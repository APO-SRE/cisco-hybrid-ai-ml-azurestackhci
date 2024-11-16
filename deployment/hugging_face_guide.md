# Hugging Face LLM Deployment Guide on Azure Arc-enabled AKS on Azure Stack HCI with Cisco UCS

This guide provides step-by-step instructions to deploy a Hugging Face Large Language Model (LLM) and expose it as an endpoint running as containers on your Azure Arc-enabled Kubernetes Service (AKS) cluster on Azure Stack HCI with Cisco UCS hardware. This deployment leverages your on-premises infrastructure while integrating with Azure services for management and monitoring.

---

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Deployment Steps](#deployment-steps)
  - [1. Set Up Azure Stack HCI and AKS](#1-set-up-azure-stack-hci-and-aks)
  - [2. Prepare the Hugging Face LLM Docker Image](#2-prepare-the-hugging-face-llm-docker-image)
  - [3. Deploy the LLM as a Container on AKS](#3-deploy-the-llm-as-a-container-on-aks)
  - [4. Expose the LLM Endpoint](#4-expose-the-llm-endpoint)
  - [5. Configure Azure Arc for Kubernetes](#5-configure-azure-arc-for-kubernetes)
  - [6. Monitor and Manage the Deployment](#6-monitor-and-manage-the-deployment)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [References](#references)
- [Additional Resources](#additional-resources)

---

## Introduction

Deploying a Hugging Face LLM on your Azure Stack HCI provides a powerful on-premises solution for running advanced language models. By leveraging Azure Arc-enabled AKS, you can manage your Kubernetes clusters and applications using familiar Azure tools while maintaining control over your data and infrastructure.

This guide walks you through deploying a Hugging Face LLM as a containerized application on your Azure Arc-enabled AKS cluster running on Azure Stack HCI with Cisco UCS servers.

---

## Prerequisites

Before you begin, ensure you have the following:

- **Azure Subscription**: An active Azure subscription.
- **Azure Stack HCI Cluster**: Deployed and configured on Cisco UCS hardware.
- **Azure Arc-enabled Kubernetes Cluster**: AKS cluster set up on Azure Stack HCI and connected to Azure Arc.
- **Docker**: Installed on your local machine for building Docker images.
- **Azure Container Registry (ACR)**: For storing your Docker images.
- **Azure CLI**: Installed and configured on your local machine.
- **Internet Connectivity**: Required for pulling Docker images and connecting to Azure services.

---

## Architecture Overview

The deployment consists of the following components:

- **Compute and Storage**: Cisco UCS servers running Azure Stack HCI and hosting the AKS cluster.
- **Containerized LLM**: A Docker container running the Hugging Face LLM.
- **Networking**: Configured to allow communication between the LLM endpoint and clients.
- **Management**: Azure Arc-enabled Kubernetes for cluster and application management.
- **Monitoring**: Azure Monitor for containers to collect logs and metrics.

---

## Deployment Steps

### 1. Set Up Azure Stack HCI and AKS

Ensure your Azure Stack HCI cluster is properly deployed on Cisco UCS hardware and that AKS is installed and connected to Azure Arc.

**References**:

- [Azure Stack HCI Deployment Guide on Cisco UCS](hci_deployment_guide.md)
- [AKS on Azure Stack HCI Deployment](aks_deployment_guide.md)


### 2. Prepare the Hugging Face LLM Docker Image

You need to create a Docker image that contains the Hugging Face LLM and exposes it as an API endpoint.

**Steps**:

1. **Create a Dockerfile**

   Create a `Dockerfile` with the following content:

   ```dockerfile
   FROM python:3.9-slim

   # Install necessary packages
   RUN pip install --no-cache-dir transformers torch flask gunicorn

   # Copy your application code
   COPY app.py /app/app.py

   # Set the working directory
   WORKDIR /app

   # Expose the port
   EXPOSE 80

   # Set the entry point
   CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
   ```

2. **Create the Application Code**

   Create an `app.py` file in the same directory with the following content:

   ```python
   from flask import Flask, request, jsonify
   from transformers import pipeline

   app = Flask(__name__)

   # Load the model
   model_name = "gpt2"  # Replace with the desired model
   generator = pipeline('text-generation', model=model_name)

   @app.route('/generate', methods=['POST'])
   def generate_text():
       data = request.get_json()
       prompt = data.get('prompt', '')
       outputs = generator(prompt, max_length=50, num_return_sequences=1)
       return jsonify(outputs)

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=80)
   ```

   **Note**: Replace `"gpt2"` with the specific Hugging Face model you wish to deploy. Be mindful of the model size and resource requirements.

3. **Build the Docker Image**

   ```bash
   docker build -t <your-acr-name>.azurecr.io/huggingface-llm:latest .
   ```

4. **Push the Docker Image to Azure Container Registry**

   - **Log in to ACR**:

     ```bash
     az acr login --name <your-acr-name>
     ```

   - **Push the Image**:

     ```bash
     docker push <your-acr-name>.azurecr.io/huggingface-llm:latest
     ```

### 3. Deploy the LLM as a Container on AKS

Now that your Docker image is ready and stored in ACR, deploy it to your AKS cluster.

**Steps**:

1. **Create a Kubernetes Deployment Manifest**

   Create a `deployment.yaml` file with the following content:

   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: huggingface-llm
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: huggingface-llm
     template:
       metadata:
         labels:
           app: huggingface-llm
       spec:
         containers:
         - name: huggingface-llm
           image: <your-acr-name>.azurecr.io/huggingface-llm:latest
           ports:
           - containerPort: 80
           resources:
             limits:
               cpu: "2"
               memory: "4Gi"
             requests:
               cpu: "1"
               memory: "2Gi"
         imagePullSecrets:
         - name: acr-secret
   ```

2. **Create an Image Pull Secret**

   - **Create the Secret**:

     ```bash
     kubectl create secret docker-registry acr-secret \
       --docker-server=<your-acr-name>.azurecr.io \
       --docker-username=<service-principal-id> \
       --docker-password=<service-principal-password> \
       --docker-email=<your-email>
     ```

     **Note**: Replace `<service-principal-id>` and `<service-principal-password>` with credentials that have access to your ACR.

3. **Apply the Deployment**

   ```bash
   kubectl apply -f deployment.yaml
   ```

### 4. Expose the LLM Endpoint

To make the LLM accessible, create a Kubernetes Service of type LoadBalancer.

**Steps**:

1. **Create a Service Manifest**

   Append the following to your `deployment.yaml` file or create a separate `service.yaml`:

   ```yaml
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: huggingface-llm-service
   spec:
     type: LoadBalancer
     selector:
       app: huggingface-llm
     ports:
     - protocol: TCP
       port: 80
       targetPort: 80
   ```

2. **Apply the Service**

   ```bash
   kubectl apply -f service.yaml
   ```

3. **Retrieve the External IP**

   ```bash
   kubectl get service huggingface-llm-service
   ```

   Wait until an external IP address is assigned.

4. **Test the Endpoint**

   Use `curl` or a REST client to test the API:

   ```bash
   curl -X POST http://<external-ip>/generate -H "Content-Type: application/json" -d '{"prompt": "Hello, world!"}'
   ```

### 5. Configure Azure Arc for Kubernetes

Ensure that your AKS cluster is connected to Azure Arc to enable management and monitoring capabilities.

**Steps**:

1. **Connect the Cluster to Azure Arc**

   If not already connected:

   ```bash
   az connectedk8s connect --name <cluster-name> --resource-group <resource-group>
   ```

2. **Install Azure Arc Extensions**

   - **Kubernetes Configuration Extension**: For GitOps and configuration management.

     ```bash
     az k8s-extension create --name k8s-configuration --cluster-name <cluster-name> --resource-group <resource-group> --cluster-type connectedClusters --extension-type Microsoft.KubernetesConfiguration
     ```

3. **Set Up Monitoring with Azure Monitor**

   - **Enable Monitoring**:

     ```bash
     az monitor log-analytics workspace create --resource-group <resource-group> --workspace-name <workspace-name>
     az monitor log-analytics workspace enable-data-collection --resource-group <resource-group> --workspace-name <workspace-name>
     az connectedk8s enable-addons --addons monitoring --name <cluster-name> --resource-group <resource-group> --workspace-id <workspace-id>
     ```

### 6. Monitor and Manage the Deployment

With Azure Arc and Azure Monitor configured, you can monitor the health and performance of your LLM deployment.

- **Access Azure Portal**: Navigate to your Kubernetes cluster resource and view insights.
- **Set Up Alerts**: Configure alerts for resource usage or application errors.
- **Use Azure Policy**: Apply policies to ensure compliance and best practices.

---

## Post-Deployment Configuration

**Scaling**:

- Adjust the number of replicas in your deployment to handle the expected load.
- Use Horizontal Pod Autoscaler (HPA) if needed.

**Security**:

- Implement network policies to restrict access.
- Use Azure Key Vault to manage secrets and certificates.

**Updates**:

- To update the LLM or application code, build a new Docker image and update the deployment.

  ```bash
  docker build -t <your-acr-name>.azurecr.io/huggingface-llm:v2 .
  docker push <your-acr-name>.azurecr.io/huggingface-llm:v2
  ```

  Update the deployment:

  ```yaml
  containers:
  - name: huggingface-llm
    image: <your-acr-name>.azurecr.io/huggingface-llm:v2
  ```

  Apply the changes:

  ```bash
  kubectl apply -f deployment.yaml
  ```

---

## References

- **Hugging Face Transformers**: [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/index)
- **AKS on Azure Stack HCI 23H2 architecture**: [Azure Stack HCI AKS Docs](https://learn.microsoft.com/en-us/azure/aks/hybrid/cluster-architecture)

---

## Additional Resources

- **Docker Documentation**: [Docker Docs](https://docs.docker.com/)
- **Azure Container Registry**: [ACR Documentation](https://learn.microsoft.com/azure/container-registry/)
- **Kubernetes Documentation**: [Kubernetes Docs](https://kubernetes.io/docs/home/)
- **Azure Monitor for Containers**: [Monitor AKS with Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/containers/container-insights-overview)

---

**Note**: This guide provides a high-level overview of the deployment process. For detailed instructions, best practices, and troubleshooting, please refer to the official documentation linked above.

---

**Disclaimer**: Ensure you have the necessary permissions and have reviewed all licensing agreements before proceeding with the deployment.
