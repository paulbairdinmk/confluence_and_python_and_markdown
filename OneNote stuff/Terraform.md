# Terraform
While both Azure Arc and HashiCorp Terraform operate in the multi-vendor, multi-cloud space, they solve fundamentally different problems. They are complementary technologies rather than direct competitors.
 * Terraform is an Infrastructure as Code (IaC) provisioning tool. It creates, updates, and destroys infrastructure resources (VMs, network interfaces, storage buckets, managed databases) across AWS, Azure, GCP, and on-premises using declarative configuration.
 * Azure Arc is an ongoing operations and management control plane. It projects existing non-Azure resources—like bare-metal servers in a private data centre, EC2 instances in AWS, or GKE clusters in GCP—into the Azure Resource Manager (ARM) so you can govern, policy-check, and monitor them as if they were native Azure resources.
## Core Comparison
| Dimension | HashiCorp Terraform |	Azure Arc |
|----|----|-----|
| Primary Focus | Provisioning & Lifecycle: Day-0/Day-1 creation and teardown of infrastructure components across cloud providers. | Governance & Operations: Day-2 management, inventory, policy enforcement, patching, and security monitoring. |
| How It Works | Declarative configuration files written in HCL (HashiCorp Configuration Language) that call provider APIs. | Lightweight agents or connected cluster extensions registered to project resources into Azure. |
| Resource Scope | Universal (Cloud services, Kubernetes, SaaS tools, networking, database users, etc.). | Compute- and platform-focused (Linux/Windows servers, Kubernetes, SQL Server, VMware/Hyper-V). |
| Target Operating State | Static/Declared: Defines what should exist at the time of execution via state tracking. | Live/Runtime: Monitors how resources behave continuously using agent-driven telemetry and live policy enforcement. |
| Vendor Neutrality | Vendor-agnostic ecosystem with equal support across AWS, Azure, GCP, and thousands of third-party platforms. | Microsoft/Azure-centric: Extends Azure control mechanisms (Azure Policy, Defender, Monitor) to external environments. |
 
## Key Operational Differences
### 1. Day-1 Provisioning vs. Day-2 Management
 * Terraform is designed to instantiate infrastructure. You write code to deploy an AWS EC2 instance, an AWS S3 bucket, and an Azure Resource Group in a single configuration.
 * Azure Arc does not create raw cloud infrastructure on AWS or GCP. Instead, once an EC2 instance or on-prem server exists, Arc installs an agent on it. From that point on, Microsoft Entra ID (RBAC), Azure Defender, and Azure Policy apply to that server.
### 2. State Tracking vs. Agent-Based Telemetry
 * Terraform relies on a declarative state file (.tfstate) to record what resources were provisioned and detect drift on demand when terraform plan is executed.
 * Azure Arc uses an agent or connected cluster integration to stream continuous heartbeats, log telemetry, compliance statuses, and system updates back to Azure Resource Manager in real time.
### 3. Multi-Vendor Scope
 * Terraform treats AWS, GCP, and Azure as equal target endpoints through open provider schemas.
 * Azure Arc acts as a "single pane of glass" centralized in Microsoft Azure. It forces non-Azure resources to conform to Azure governance frameworks.
## How They Work Together
In enterprise architectures across multiple vendors, Terraform and Azure Arc are commonly used in tandem:
 * Terraform provisions the base layer: You run Terraform to build virtual machines or Kubernetes clusters across AWS, GCP, and on-premises vSphere environments.
 * Terraform bootstraps Azure Arc: During VM provisioning, Terraform runs a startup script (via user_data or custom extension) to install the Azure Arc connected machine agent on the newly created server.
 * Azure Arc governs the runtime: Once the server is live, security teams use Azure Policy, Microsoft Defender for Cloud, and Azure Monitor to keep the multicloud estate compliant and monitored centrally.
