# AKS Deployment Guide on Azure Stack HCI with Azure Arc

This guide provides step-by-step instructions for deploying an AKS cluster on Azure Stack HCI using Azure Arc, with a focus on network requirements, IP address planning, and logical network setup before creating the AKS cluster.

---

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Deployment Steps](#deployment-steps)
  - [1. AKS Network Requirements](#1-aks-network-requirements)
  - [2. IP Address Planning for AKS](#2-ip-address-planning-for-aks)
  - [3. Create Logical Networks for AKS Clusters](#3-create-logical-networks-for-aks-clusters)
  - [4. Install Azure CLI Extensions](#4-install-azure-cli-extensions)
  - [5. Register Resource Providers](#5-register-resource-providers)
  - [6. Create a Kubernetes Cluster](#6-create-a-kubernetes-cluster)
  - [7. Connect to the Kubernetes Cluster](#7-connect-to-the-kubernetes-cluster)
  - [8. Deploy a Sample Application](#8-deploy-a-sample-application)
- [References](#references)

---

## Introduction

This guide focuses on creating a Kubernetes cluster on Azure Stack HCI, with preliminary steps for ensuring proper networking and IP address configuration. The cluster will be Azure Arc-connected, allowing for management via Azure.

---

## Prerequisites

Before beginning, ensure you have:
- **Azure Stack HCI Already Deployed**
  - [Azure Stack HCI Deployment](hci_deployment_guide.md)
- **Azure Subscription ID**
- **Custom Location ID**: Set up during Azure Stack HCI deployment. Use the command below if needed:
  ```bash
  az customlocation show --name "<custom location name>" --resource-group <resource group> --query "id" -o tsv
  ```
- **Network ID**: The logical network ID in Azure Stack HCI.
  ```bash
  az stack-hci-vm network lnet show --name "<lnet name>" --resource-group <resource group> --query "id" -o tsv
  ```
- **Microsoft Entra Group ID**: For cluster admin access. Ensure your ID is included in this group.
- **kubectl** installed on your development machine.
- **Azure CLI**: Updated with the necessary extensions.

---

## Deployment Steps

### 1. AKS Network Requirements

Ensure your network meets the following requirements for AKS enabled by Azure Arc:

- **AKS Cluster VMs**: Assign static IPs for each Kubernetes node.
- **Control Plane IP**: Reserve an immutable IP for the Kubernetes control plane. This IP must be within the logical network's address prefix but outside the IP pool range.
- **Load Balancer IPs**: Reserve a set of IP addresses for the load balancer service to avoid IP conflicts with the control plane and logical network.
- **Proxy and DNS Settings**: Confirm your DNS server can resolve the Azure Stack HCI cluster FQDN. Adjust proxy settings as needed.
  
For more details, see [AKS enabled by Azure Arc Network Requirements](https://learn.microsoft.com/en-us/azure/aks/hybrid/aks-hci-network-system-requirements).

### 2. IP Address Planning for AKS

Plan the IP addresses as follows:

- **VM IPs**: Reserve one IP per worker node in the Kubernetes cluster.
- **Upgrade IPs**: Reserve one IP per cluster for Kubernetes version upgrades.
- **Control Plane IPs**: Reserve one IP per cluster for control plane management.
- **Load Balancer IPs**: Reserve IPs for Kubernetes services as needed.

Refer to [IP Address Planning Requirements](https://learn.microsoft.com/en-us/azure/aks/hybrid/aks-hci-ip-address-planning) for detailed guidance.

### 3. Create Logical Networks for AKS Clusters

To create a logical network on Azure Stack HCI, follow these steps:

1. **List VM Switches**: Identify the VM switch to associate with the logical network.
   ```powershell
   Get-VmSwitch -SwitchType External
   ```
2. **Create Logical Network**: Use the following CLI command to create a logical network with static IP configuration:
   ```bash
   az stack-hci-vm network lnet create --name "<logical_network_name>" \
     --resource-group $resource_group --subscription $subscription \
     --custom-location $customlocationID --vm-switch-name "<vm_switch_name>" \
     --address-prefixes "10.220.32.16/24" --dns-servers "10.220.32.16 10.220.32.17" \
     --gateway "10.220.32.1" --ip-allocation-method "Static" \
     --ip-pool-start "10.220.32.18" --ip-pool-end "10.220.32.38"
   ```

### 4. Install Azure CLI Extensions

Install the necessary Azure CLI extensions for AKS Arc and custom locations.

```bash
az extension add -n aksarc --upgrade
az extension add -n customlocation --upgrade
az extension add -n stack-hci-vm --upgrade
az extension add -n connectedk8s --upgrade
```

### 5. Register Resource Providers

Register the required Azure providers:

```bash
az provider register --namespace Microsoft.ExtendedLocation --wait
az provider register --namespace Microsoft.Web --wait
az provider register --namespace Microsoft.KubernetesConfiguration --wait
```

### 6. Create a Kubernetes Cluster

Use the `az aksarc create` command to create your Kubernetes cluster in AKS Arc.

```bash
az aksarc create -n $aksclustername -g $resource_group \
    --custom-location $customlocationID \
    --vnet-ids $logicnetId \
    --aad-admin-group-object-ids $aadgroupID \
    --generate-ssh-keys \
    --load-balancer-count 0 \
    --control-plane-ip $controlplaneIP
```

### 7. Connect to the Kubernetes Cluster

To connect to the cluster, run the following command to open a proxy connection and download the kubeconfig.

```bash
az connectedk8s proxy --name $aksclustername --resource-group $resource_group --file .\aks-arc-kube-config
```

Verify the connection with:

```bash
kubectl get node -A --kubeconfig .\aks-arc-kube-config
```

### 8. Deploy a Sample Application

Deploy a sample multi-container application (e.g., web front-end and Redis backend) to verify your cluster setup.

---

## References

- [AKS on Azure Stack HCI Network Requirements](https://learn.microsoft.com/en-us/azure/aks/hybrid/aks-hci-network-system-requirements)
- [IP Address Planning for AKS](https://learn.microsoft.com/en-us/azure/aks/hybrid/aks-hci-ip-address-planning)
- [Create Kubernetes Clusters using Azure CLI](https://learn.microsoft.com/en-us/azure/aks/hybrid/aks-create-clusters-cli)

---

**Disclaimer**: Ensure you have the necessary permissions and have reviewed all licensing agreements before proceeding with the deployment.

---
