# Getting Started Guide

This guide provides step-by-step instructions to help you set up the foundational infrastructure for the **Cisco AI-Driven Enterprise Data Architecture** on Azure Stack HCI with Cisco UCS. It focuses on:

- Deploying Azure Stack HCI on Cisco UCS hardware.
- Setting up Azure Kubernetes Service (AKS) on Azure Stack HCI.
- Configuring Azure and Cisco resources required for the solution.

For detailed deployment of AI/ML workloads and Generative AI applications, please refer to the specific deployment guides listed in the [Next Steps](#next-steps) section.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Setup Steps](#setup-steps)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Deploy Azure Stack HCI on Cisco UCS](#2-deploy-azure-stack-hci-on-cisco-ucs)
  - [3. Set Up AKS on Azure Stack HCI](#3-set-up-aks-on-azure-stack-hci)
  - [4. Configure Cisco Networking and Security Products](#4-configure-cisco-networking-and-security-products)
- [Next Steps](#next-steps)
- [Additional Resources](#additional-resources)
- [Contributing](#contributing)
- [License](#license)

---

## Prerequisites

Before you begin, ensure you have the following:

- **Cisco UCS Hardware**: Access to Cisco UCS servers (e.g., M7 C220s and C240s).
- **Azure Subscription**: With permissions to create resources.
- **Installed Tools**:
  - [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
  - [PowerShell 7](https://learn.microsoft.com/powershell/scripting/install/installing-powershell)
  - [Windows Admin Center](https://www.microsoft.com/windows-server/windows-admin-center)
- **Basic Knowledge** of Azure services and Cisco technologies used in this architecture.

---

## Architecture Overview

For a detailed understanding of the architecture and its components, please refer to the [Architecture Overview](architecture_overview.md).

---

## Setup Steps

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

---

### 2. Deploy Azure Stack HCI on Cisco UCS

Deploy Azure Stack HCI on your Cisco UCS hardware to provide the foundational infrastructure.

- **Deployment Guide**: [Azure Stack HCI Deployment Guide](/deployment/hci_deployment_guide.md)

**High-Level Steps**:

1. **Prepare the Hardware**:
   - Ensure that Cisco UCS servers are properly installed and connected.
   - Verify firmware versions and hardware compatibility.

2. **Install Azure Stack HCI**:
   - Download the Azure Stack HCI installation media.
   - Install Azure Stack HCI on each node following Microsoft's guidelines.

3. **Set Up Networking**:
   - Configure networking settings for storage, management, and VM traffic.
   - Ensure that network adapters are properly teamed and configured.

4. **Create the Cluster**:
   - Use Windows Admin Center or PowerShell to create an Azure Stack HCI cluster.
   - Validate the cluster configuration.

---

### 3. Set Up AKS on Azure Stack HCI

Deploy Azure Kubernetes Service (AKS) on Azure Stack HCI to run containerized workloads.

- **Deployment Guide**: [AKS on Azure Stack HCI Deployment Guide](/deployment/aks_deployment_guide.md)

**High-Level Steps**:

1. **Install AKS on Azure Stack HCI**:
   - Use PowerShell or Windows Admin Center to install AKS on your cluster.

2. **Configure Kubernetes Cluster**:
   - Create a Kubernetes cluster using AKS on Azure Stack HCI.
   - Configure node pools and networking settings.

3. **Validate the Deployment**:
   - Ensure that the Kubernetes cluster is up and running.
   - Use `kubectl` to interact with the cluster.

---

### 4. Configure Cisco Networking and Security Products

Set up and configure the Cisco networking and security components to ensure secure and efficient connectivity.

**Components and Deployment Guides**:

- **Cisco Intersight**:
  - **Deployment Guide**: [Intersight Deployment](https://intersight.com/help/saas/home)

- **Cisco Catalyst SD-WAN**:
  - **Deployment Guide**: [Catalyst SD-WAN Deployment](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/cisco-sd-wan-overlay-network-bringup.html)
- **Cisco Multicloud Defense**:
  - **Deployment Guide**: [Multicloud Defense Deployment](https://www.cisco.com/c/en/us/td/docs/security/cdo/multicloud-defense/user-guide/cisco-multicloud-defense-user-guide.html)
- **Cisco ThousandEyes**:
  - **Deployment Guide**: [ThousandEyes Deployment](https://docs.thousandeyes.com/product-documentation/global-vantage-points/enterprise-agents/installing)
- **Robust Intelligence**:
  - **Deployment Guide**: [Robust Intelligence Deployment](https://docs.robustintelligence.com/en/2.3-stable/deployment/installation.html)
- **Cisco Secure Firewall**:
  - **Deployment Guide**: [Secure Firewall Deployment](https://www.cisco.com/c/en/us/support/security/firepower-ngfw/products-installation-and-configuration-guides-list.html)

**High-Level Steps**:

1. **Integrate Cisco Intersight**:
   - Use Cisco Intersight for unified infrastructure management.
   - Connect your UCS hardware to Intersight for monitoring and automation.
     
2. **Install and Configure Networking Equipment**:
   - Set up Cisco routers, switches, and SD-WAN appliances.
   - Configure network settings to support the hybrid environment.

3. **Implement Security Measures**:
   - Deploy firewalls, intrusion prevention systems, and other security appliances.
   - Configure security policies and access controls.

4. **Set Up Monitoring and Visibility Tools**:
   - Install Cisco ThousandEyes for network visibility.
   - Integrate monitoring solutions with your environment.



---

## Next Steps

With the foundational infrastructure in place, you can proceed to deploy specific workloads and applications.

- **Chat App with Azure OpenAI Deployment**:
  - **Guide**: [Chat App Deployment Guide](/deployment/aoai_chat_deployment_guide.md)
- **Hugging Face Deployment**:
  - **Guide**: [Hugging Face Deployment Guide](/deployment/hugging_face_guide.md)
- **Machine Learning Deployment**:
  - **Guide**: [Machine Learning Deployment Guide](/deployment/ml_deployment_guide.md)
- **Running ML Workloads on Cisco Azure Stack HCI**:
  - **Guide**: [Running ML Workloads on Cisco Azure Stack HCI](running_ml_workloads_guide.md)

---

## Contributing

We welcome contributions to enhance this project. Please read our [Contribution Guidelines](CONTRIBUTING.md) to get started.

---

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](../LICENSE) file for details.

---

# Summary

In this updated `getting_started.md`, the focus is on setting up the foundational infrastructure, including:

- **Deployment of Azure Stack HCI on Cisco UCS hardware**.
- **Setup of AKS on Azure Stack HCI**.
- **Configuration of Cisco networking and security products**.
- **Setup of Azure resources, including the Azure Machine Learning workspace and Azure Arc integration**.

The guide provides high-level steps and points users to the specific deployment guides for detailed instructions. It refrains from diving into the deployment of AI/ML workloads or Generative AI applications, which are covered in the subsequent sections listed under [Next Steps](#next-steps).

This approach ensures that users can set up the necessary infrastructure and resources before proceeding to deploy specific workloads, aligning with your request.

---

**Let me know if you need further adjustments or additional information!**
