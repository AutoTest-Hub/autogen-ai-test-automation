---

# AI Test Automation Platform: Hybrid SaaS & On-Premise Architecture

**Author**: Manus AI
**Date**: September 23, 2025
**Version**: 1.0

## 1. Overview

This document outlines the architectural design for the AI Test Automation Platform to support both **Multi-Tenant SaaS** and **Single-Tenant On-Premise** deployment models. The primary goal is to maintain a unified codebase while providing the flexibility, security, and data isolation required by different customer segments. This hybrid approach allows us to serve a broad market, from startups and SMBs who prefer a managed cloud solution to large enterprises with strict data sovereignty and compliance requirements.

## 2. Core Architectural Principles

The architecture is founded on the following principles:

- **Unified Codebase**: A single codebase for the application core, API, and frontend will be used for both deployment models to streamline development, maintenance, and feature parity.
- **Configuration-Driven Deployment**: The application's behavior and features will adapt based on a simple `DEPLOYMENT_MODE` environment variable (`SaaS` or `OnPrem`).
- **Strict Data Isolation**: In the SaaS model, all customer data is logically separated and secured at every layer of the stack, from the database to the API.
- **Scalability**: The architecture is designed to scale horizontally to support a growing number of tenants in the SaaS model and handle large workloads in On-Premise installations.
- **Extensibility**: The design allows for the easy addition of new features, some of which may be specific to a particular deployment model.

## 3. Deployment Models

| Feature                  | Multi-Tenant SaaS                               | Single-Tenant On-Premise                             |
| ------------------------ | ----------------------------------------------- | ---------------------------------------------------- |
| **Target Customer**      | Startups, SMBs, teams preferring managed services | Large enterprises, government, regulated industries  |
| **Infrastructure**       | Managed by us on a public cloud (e.g., AWS, GCP) | Managed by the customer in their own data center/VPC |
| **Database**             | Shared PostgreSQL database with logical isolation | Dedicated PostgreSQL instance for a single customer  |
| **Data Isolation**       | Achieved via `customer_id` scoping (Row-Level)  | Physical isolation at the database and network level |
| **Subscription & Billing** | Fully integrated and managed within the platform  | Handled via enterprise licensing; features are unlocked |
| **Updates & Maintenance**  | Handled by us, seamless for the customer       | Customer-managed update process (e.g., via Docker images) |
| **Customization**        | Limited to user-level settings                  | High (custom branding, integrations, configurations) |

## 4. Database Architecture: A Hybrid Approach

The PostgreSQL database schema is designed to be identical for both models. The key to supporting both is the consistent use of a `customer_id` (or `tenant_id`) on all relevant tables.

### 4.1. Multi-Tenancy Strategy

We will employ a **Logical Data Isolation** strategy within a shared database for the SaaS model.

- **Tenant Identifier**: Every table containing customer-specific data (e.g., `applications`, `test_executions`, `test_suites`) will have a non-nullable `customer_id` foreign key referencing the `customers` table.
- **Query Scoping**: Every database query executed by the application will be automatically and mandatorily filtered by the `customer_id` of the authenticated user. This will be enforced at the ORM/service layer to prevent any possibility of data leakage between tenants.
- **On-Premise Simplification**: In an On-Premise deployment, the database will contain only one entry in the `customers` table. While the `customer_id` column will still exist, all queries will implicitly scope to this single customer.

### 4.2. Schema Modifications for Hybrid Support

The existing `schema.sql` is already well-suited for this model. The key is the consistent presence of `customer_id`:

```sql
-- Example: test_executions table
CREATE TABLE test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    -- This column is the key to our hybrid strategy
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    -- ... other columns
);

-- Example: applications table
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    -- All customer-owned resources are tied back to the customer
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    -- ... other columns
);
```

Tables that are specific to the SaaS model, such as `subscription_plans`, will simply be unused or hidden in an On-Premise deployment.

## 5. Application & API Layer

The backend API (FastAPI) will be the central point for enforcing the hybrid logic.

### 5.1. Configuration Management

The application will read its configuration from environment variables:

- `DEPLOYMENT_MODE`: Can be `SaaS` (default) or `OnPrem`.
- `DATABASE_URL`: Connection string to the PostgreSQL database.
- `SECRET_KEY`: For signing JWTs.
- `ONPREM_CUSTOMER_ID` (On-Prem only): The default UUID for the single customer tenant.

### 5.2. Tenant-Aware Logic

- **Authentication**: Upon login, a JWT will be issued containing the `user_id` and `customer_id`.
- **API Endpoints**: A middleware or dependency injection system will extract the `customer_id` from the JWT and make it available to all service layer functions.
- **Service Layer Enforcement**: All database service functions (e.g., `get_customer_applications`) will require a `customer_id` argument and include it in the `WHERE` clause of their queries.

```python
# Example of enforced tenant isolation in the service layer
class ApplicationService:
    @staticmethod
    def get_customer_applications(db: Session, customer_id: uuid.UUID) -> List[Application]:
        """Get all applications for a specific customer"""
        # The query is explicitly filtered by customer_id, preventing data leaks.
        return db.query(Application).filter(
            Application.customer_id == customer_id
        ).all()
```

### 5.3. Feature Flagging

Based on the `DEPLOYMENT_MODE`, certain API endpoints and features will be conditionally enabled or disabled.

- **SaaS Mode**: Endpoints for billing, subscription management, and user registration will be active.
- **On-Prem Mode**: These endpoints will be disabled (return a 404 or 403). The system will assume a single, pre-configured enterprise license.

## 6. Frontend (UI) Layer

The React dashboard will adapt its UI based on the deployment mode.

- **API-Driven UI**: The frontend will query a `/api/v1/system/config` endpoint on startup. This endpoint will return the `DEPLOYMENT_MODE` and other public configurations.
- **Conditional Rendering**: React components related to billing, subscription plans, or multi-customer management will be conditionally rendered based on the mode.
- **Branding**: In On-Prem mode, the UI can be configured to display the customer's logo and branding, with settings loaded from the database or a config file.

## 7. Deployment & Operations

### 7.1. SaaS Deployment

- **Infrastructure**: Deployed on a cloud provider using Kubernetes for orchestration and scalability.
- **Database**: A managed PostgreSQL service (e.g., AWS RDS, Google Cloud SQL) will be used for high availability and automated backups.
- **CI/CD**: A fully automated pipeline will handle testing and deployment of new versions to the SaaS environment.

### 7.2. On-Premise Deployment

- **Packaging**: The entire platform (API, Web UI, Agents) will be packaged as a set of Docker images and delivered with a `docker-compose.yml` file for easy setup.
- **Installation**: The customer will run a deployment script that configures the environment, initializes the database for a single tenant, and starts the services.
- **Updates**: Updates will be delivered as new sets of Docker images. A script will be provided to handle the update process, including database migrations.

## 8. Conclusion

This hybrid architectural design provides a robust and flexible foundation for the AI Test Automation Platform. By centralizing the deployment logic in the configuration and enforcing strict data isolation at the API and database layers, we can maintain a single, efficient codebase while catering to the distinct needs of both SaaS and On-Premise customers. This strategy positions the platform for broad market adoption and long-term maintainability.

---

