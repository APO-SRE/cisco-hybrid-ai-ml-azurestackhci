# Azure Stack HCI Deployment Guide on Cisco UCS

This guide provides step-by-step instructions for deploying Azure Stack HCI, version 23H2, on Cisco UCS hardware. It references both Microsoft's and Cisco's official documentation to ensure a smooth and successful deployment.

---

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Deployment Steps](#deployment-steps)
  - [1. Plan and Prepare](#1-plan-and-prepare)
  - [2. Install Windows Server on Cisco UCS](#2-install-windows-server-on-cisco-ucs)
  - [3. Configure Networking](#3-configure-networking)
  - [4. Install Azure Stack HCI](#4-install-azure-stack-hci)
  - [5. Create the Cluster](#5-create-the-cluster)
  - [6. Validate and Register the Cluster](#6-validate-and-register-the-cluster)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [References](#references)
- [Additional Resources](#additional-resources)
- [Support](#support)

---

## Introduction

Azure Stack HCI is a hyperconverged infrastructure (HCI) solution that combines software-defined compute, storage, and networking on industry-standard servers. Deploying Azure Stack HCI on Cisco UCS servers provides a robust, scalable, and high-performance platform for running virtualized workloads and hybrid cloud services.

This guide walks you through the deployment process, highlighting key steps and considerations specific to Cisco UCS hardware.

---

## Prerequisites

Before you begin, ensure you have the following:

**Cisco UCS Hardware:**

- Cisco UCS C-Series servers (e.g., M7 C220 or C240) compatible with Azure Stack HCI.
- Latest firmware and BIOS updates applied.

**Networking Equipment:**

- Compatible network switches and adapters.

**Software:**

- Windows Server 2022 Datacenter edition or Azure Stack HCI, version 23H2 installation media.

**Licenses:**

- Valid licenses for Windows Server or Azure Stack HCI.

**Administrative Access:**

- Access to Cisco Integrated Management Controller (CIMC) for each server.
- Access to network infrastructure for configuration.

**Internet Connectivity:**

- Required for downloading updates and registering the cluster with Azure.

---

## Architecture Overview

The deployment consists of the following components:

- **Compute and Storage**: Cisco UCS servers running Azure Stack HCI, providing virtualized compute and storage resources.
- **Networking**: High-speed network connectivity using Ethernet adapters and switches for storage replication, virtual machine traffic, and management.
- **Management**: Windows Admin Center for managing the cluster and workloads.
- **Hybrid Services**: Integration with Azure for hybrid capabilities like Azure Monitor, Azure Backup, and more.

---

## Deployment Steps

### 1. Plan and Prepare

**a. Review Deployment Guides**

- **Microsoft Deployment Introduction:**
  - [Azure Stack HCI Deployment Introduction](https://learn.microsoft.com/azure-stack/hci/deploy/deployment-introduction)
- **Cisco Deployment Guide:**
  - [Cisco Azure Stack HCI Deployment Guide](https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/UCS_CVDs/ucs_mas_hci_23H2.html)

**b. Verify Hardware Compatibility**

- Ensure your Cisco UCS servers are listed in the [Azure Stack HCI Catalog](https://azurestackhcisolutions.azure.microsoft.com/#/catalog?Search=cisco).

**c. Gather Requirements**

- **Network Configuration:**
  - IP addresses for management, storage, and VM networks.
- **Domain Information:**
  - Active Directory domain details for joining servers to the domain.

**d. Firmware and Driver Updates**

- Update firmware and drivers using the [Cisco Host Upgrade Utility (HUU)](https://www.cisco.com/c/en/us/support/servers-unified-computing/ucs-c-series-rack-servers/products-release-notes-list.html).

---

### 2. Install Windows Server on Cisco UCS

**a. Access CIMC**

- Log in to the Cisco Integrated Management Controller for each server.

**b. Mount Installation Media**

- Mount the Windows Server or Azure Stack HCI ISO using virtual media in CIMC.

**c. Install the Operating System**

- Boot from the mounted ISO and follow the installation prompts.
- Choose **Windows Server 2022 Datacenter** or **Azure Stack HCI** as the edition.
- Partition disks as needed.

**d. Configure Initial Settings**

- Set a strong administrator password.
- Configure the server's hostname.

---

### 3. Configure Networking

**a. Install Network Adapters**

- Ensure that all required network adapters are installed and recognized by the operating system.

**b. Install Latest Network Drivers**

- Download and install the latest network drivers from Cisco's support site.

**c. Configure Network Interfaces**

- Assign IP addresses to management interfaces.
- Disable any unused adapters.

**d. Set Up Network Teaming or SET**

- Use Switch Embedded Teaming (SET) or NIC Teaming for redundancy and bandwidth aggregation.
- Reference: [Network ATC and SET on Azure Stack HCI](https://learn.microsoft.com/en-us/azure-stack/hci/concepts/network-atc-overview?pivots=azure-stack-hci)

---

### 4. Install Azure Stack HCI

#### a. Download the Azure Stack HCI Software

1. Sign in to the [Azure portal](https://portal.azure.com) with your Azure account.
2. In the search bar, enter **Azure Stack HCI** and select it under the **Services** category.
3. On the **Get started** page, under the **Download software** tile, select **Download Azure Stack HCI**.
4. Choose **Azure Stack HCI, version 23H2** and **English** as the language. 
   - Note: **English** is currently the only supported language for Azure Stack HCI.
5. Review the terms and click **Download Azure Stack HCI** to start downloading the ISO file.

#### b. Install the Azure Stack HCI Operating System

1. Mount the downloaded ISO on each server.
2. Boot from the ISO and follow the installation prompts.
   - Select **Custom: Install the newer version of Azure Stack HCI only (advanced)**. Note that upgrade installations are not supported.
3. Set the local administrator password to meet Azure complexity requirements (at least 12 characters with mixed case, numeral, and special character).
4. Configure network settings and drivers using the **SConfig** tool. 

#### c. Configure the Operating System using SConfig

- **Important**: Avoid using SConfig for Windows Updates to prevent deployment failures.
- Use SConfig to set up VLAN IDs, DHCP, and DNS settings as required.
- For valid time synchronization, configure an NTP server using:
  ```powershell
  w32tm /config /manualpeerlist:"ntpserver.contoso.com" /syncfromflags:manual /update
  ```

---

### 5. Create the Cluster

**a. Install Required Roles and Features**

- Open PowerShell as an administrator and run:
  ```powershell
  Install-WindowsFeature -Name Failover-Clustering, RSAT-Clustering-PowerShell, Data-Center-Bridging
  ```

**b. Validate the Cluster Configuration**

- Run the cluster validation wizard:
  ```powershell
  Test-Cluster -Node Server1, Server2 -Include "Storage Spaces Direct", "Inventory", "Network", "System Configuration"
  ```

**c. Create the Cluster**

- Use PowerShell to set up the cluster:
  ```powershell
  New-Cluster -Name ClusterName -Node Server1, Server2 -StaticAddress ClusterIP
  ```

**d. Enable Storage Spaces Direct**

- Enable Storage Spaces Direct on the cluster:
  ```powershell
  Enable-ClusterStorageSpacesDirect
  ```

---

### 6. Validate and Register the Cluster

**a. Register the Cluster with Azure Arc**

1. Register required resource providers in the Azure portal:
   - **Microsoft.HybridCompute**
   - **Microsoft.GuestConfiguration**
   - **Microsoft.HybridConnectivity**
   - **Microsoft.AzureStackHCI**
2. On each server, install required PowerShell modules and run the registration script to register with Azure Arc.

3. Verify that the servers are registered with Arc in the Azure portal.

**b. Set Azure Role Permissions**

- Assign the following permissions for deployment:
  - Azure Stack HCI Administrator
  - Reader
  - Key Vault Data Access Administrator
  - Key Vault Secrets Officer
  - Key Vault Contributor
  - Storage Account Contributor
  - Cloud Application Administrator

---

## Post-Deployment Configuration

**a. Set Up Networking for VMs**

- Create virtual switches for virtual machine traffic.
- Configure VLANs and QoS policies as needed.

**b. Deploy Virtual Machines**

- Use Hyper-V Manager or Windows Admin Center to create and manage VMs.

**c. Enable Hybrid Services**

- Configure Azure services such as Azure Backup, Azure Monitor, and Azure Site Recovery.

---

## References

**Microsoft Documentation:**

- [Azure Stack HCI Documentation](https://learn.microsoft.com/azure-stack/hci/)
- [Deployment Introduction](https://learn.microsoft.com/azure-stack/hci/deploy/deployment-introduction)


**Cisco Documentation:**

- [Cisco Azure Stack HCI Deployment Guide](https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/UCS_CVDs/ucs_mas_hci_23H2.html)
 

---

## Additional Resources

- [Windows Admin Center](https://www.microsoft.com/windows-server/windows-admin-center)
- [Switch Embedded Teaming (SET)](https://learn.microsoft.com/en-us/azure-stack/hci/deploy/network-atc?tabs=22H2&pivots=azure-stack-hci)
- [Azure Hybrid Services](https://learn.microsoft.com/en-us/azure-stack/hci/hybrid-capabilities-with-azure-services)

---

## Support

If you encounter issues during deployment:

**Microsoft Support:**

- [Azure Support](https://azure.microsoft.com/support/options/)
- [Azure Stack HCI Community](https://techcommunity.microsoft.com/t5/azure-stack-hci/bd-p/AzureStackHCI)

**Cisco Support:**

- [Cisco Support & Downloads](https://www.cisco.com/c/en/us/support/index.html)

---

**Disclaimer:** Ensure you have the necessary permissions and have reviewed all licensing agreements before proceeding with the deployment.

