# AI Test Automation Platform - Deployment Guide

**Version**: 1.0.0
**Author**: Manus AI
**Date**: September 23, 2025

## 1. Introduction

This guide provides comprehensive instructions for deploying the AI Test Automation Platform in both **SaaS (Software as a Service)** and **On-Premises (OnPrem)** environments. The platform is designed with a hybrid architecture to support both deployment models, ensuring flexibility, security, and scalability for all types of customers.

### 1.1. Architecture Overview

The platform consists of three main components:

- **Web Dashboard**: A React-based user interface for managing applications, creating tests, and viewing results.
- **API Backend**: A FastAPI-based service layer that orchestrates AI agents, manages data, and handles business logic.
- **PostgreSQL Database**: A secure and scalable database for storing all platform data.

For a detailed architecture overview, please refer to the [ARCHITECTURE.md](ARCHITECTURE.md) document.

### 1.2. Deployment Models

| Feature | SaaS Deployment | On-Premises Deployment |
| :--- | :--- | :--- |
| **Hosting** | Managed by us on a secure cloud infrastructure | Hosted by the customer in their own environment |
| **Data Storage** | Multi-tenant database with strict data isolation | Single-tenant database within customer's network |
| **Maintenance** | Handled by our team (updates, security, etc.) | Managed by the customer's IT team |
| **Customization** | Limited to subscription plan features | Full customization and branding options |
| **Security** | SOC 2 Type II compliant, managed security | Customer-managed security, air-gapped support |
| **Authentication** | Email/password, social logins, MFA | LDAP/SAML integration, SSO |

## 2. Prerequisites

Before you begin, ensure you have the following prerequisites installed:

- **Git**: For cloning the repository.
- **Docker**: For containerized deployment (recommended).
- **Docker Compose**: For orchestrating multi-container applications.
- **Node.js & npm**: For running the web dashboard in development.
- **Python 3.10+**: For running the API backend in development.

## 3. SaaS Deployment

The SaaS deployment is managed by our team. Customers can sign up and start using the platform immediately. This section is for informational purposes to understand the SaaS architecture.

### 3.1. SaaS Architecture

- **Cloud Provider**: AWS, Azure, or Google Cloud.
- **Container Orchestration**: Kubernetes (EKS, AKS, or GKE).
- **Database**: Managed PostgreSQL service (e.g., Amazon RDS).
- **CI/CD**: Automated builds, tests, and deployments using GitHub Actions.
- **Monitoring**: Prometheus, Grafana, and custom alerting.

### 3.2. Customer Onboarding

1. **Sign Up**: Customers register on our public website.
2. **Select Plan**: Choose a subscription plan (e.g., Free, Pro, Enterprise).
3. **Add Application**: Onboard their web applications for testing.
4. **Create Tests**: Use the AI-powered interface to create automated tests.

## 4. On-Premises Deployment

This section provides detailed instructions for deploying the platform in your own environment.

### 4.1. Step 1: Clone the Repository

```bash
git clone https://github.com/AutoTest-Hub/autogen-ai-test-automation.git
cd autogen-ai-test-automation
```

### 4.2. Step 2: Configure the Environment

Create a `.env` file in the root directory and configure the following variables:

```env
# Deployment Mode
DEPLOYMENT_MODE=OnPrem

# Database Configuration
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=ai_test_automation
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_SSL_MODE=require

# API Backend Configuration
SECRET_KEY=your-strong-secret-key

# Web Dashboard Configuration
VITE_ONPREM_API_URL=http://your-api-backend-url
```

### 4.3. Step 3: Database Setup

1. **Provision a PostgreSQL database** (version 13+).
2. **Create a dedicated user and database** for the platform.
3. **Apply the database schema**:

   ```bash
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME < database/schema_secure.sql
   ```

4. **Apply On-Premises specific configuration**:

   ```bash
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME < database/config/onprem_config.sql
   ```

### 4.4. Step 4: Deployment with Docker (Recommended)

This is the easiest and most reliable way to deploy the platform.

1. **Build the Docker images**:

   ```bash
   docker-compose build
   ```

2. **Start the services**:

   ```bash
   docker-compose up -d
   ```

3. **Access the platform**:

   - **Web Dashboard**: `http://localhost` (or your server's IP)
   - **API Backend**: `http://localhost:8000`

### 4.5. Step 5: Manual Deployment (for Development)

**1. Start the API Backend**:

```bash
# Install dependencies
pip install -r api/requirements.txt

# Start the server
python api/server_secure.py
```

**2. Start the Web Dashboard**:

```bash
# Navigate to the dashboard directory
cd web-dashboard

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4.6. On-Premises Configuration

- **LDAP/SAML Integration**: Configure your identity provider in the `Settings` section of the web dashboard.
- **Custom Branding**: Update the branding assets in `web-dashboard/src/assets/branding/`.
- **Email Server**: Configure your SMTP server for email notifications.

## 5. Security and Compliance

The platform is designed with a security-first approach and is SOC 2 Type II compliant by default.

- **Data Encryption**: All sensitive data is encrypted at rest and in transit.
- **Role-Based Access Control (RBAC)**: Granular permissions for all users.
- **Audit Logging**: Comprehensive audit trails for all actions.
- **Security Monitoring**: Real-time security event detection and alerting.

For more details, please refer to the [SOC_COMPLIANCE.md](SOC_COMPLIANCE.md) document.

## 6. Getting Support

- **SaaS Customers**: Contact our support team through the web dashboard.
- **On-Premises Customers**: Refer to your enterprise support agreement.

---

This deployment guide provides a comprehensive overview of how to deploy and manage the AI Test Automation Platform. For any further questions, please refer to the project documentation or contact our support team.

