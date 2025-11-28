# Deployment Guide

This guide provides in-depth instructions for deploying the AI Test Automation SaaS Platform.

## Deployment Options

- **Docker Compose**: For local development and testing.
- **Kubernetes**: For production and scalable deployments.

## Docker Compose Deployment

1.  **Prerequisites**:
    - Docker
    - Docker Compose

2.  **Deployment**:
    ```bash
    ./scripts/deploy.sh
    ```

3.  **Cleanup**:
    ```bash
    ./scripts/deploy.sh cleanup
    ```

## Kubernetes Deployment

1.  **Prerequisites**:
    - Kubernetes cluster
    - `kubectl`

2.  **Deployment**:
    ```bash
    ./scripts/deploy.sh kubernetes
    ```

3.  **Cleanup**:
    ```bash
    ./scripts/deploy.sh cleanup
    ```

## Configuration

- **Environment Variables**: Configure the platform using environment variables in the `docker-compose.yml` or `k8s/deployment.yaml` files.
- **Requirements Templates**: Add or modify requirements templates in the `requirements` directory.

## Monitoring

- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3001` (admin/admin123)

