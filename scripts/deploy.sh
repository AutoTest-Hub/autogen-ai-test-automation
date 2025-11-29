#!/bin/bash
set -e

# AI Test Automation SaaS Platform - Deployment Script
# ====================================================

echo "🚀 AI Test Automation SaaS Platform Deployment"
echo "=============================================="

# Configuration
DEPLOYMENT_TYPE=${1:-docker-compose}
ENVIRONMENT=${2:-production}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if [ "$DEPLOYMENT_TYPE" = "docker-compose" ]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker is not installed. Please install Docker first."
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            log_error "Docker Compose is not installed. Please install Docker Compose first."
            exit 1
        fi
        
        log_success "Docker and Docker Compose are available"
    elif [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl is not installed. Please install kubectl first."
            exit 1
        fi
        
        if ! kubectl cluster-info &> /dev/null; then
            log_error "Kubernetes cluster is not accessible. Please configure kubectl."
            exit 1
        fi
        
        log_success "Kubernetes cluster is accessible"
    fi
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Create necessary directories
    mkdir -p work_dir tests pages logs database monitoring/grafana/{dashboards,datasources} nginx/ssl
    
    # Generate SSL certificates for development
    if [ ! -f nginx/ssl/cert.pem ]; then
        log_info "Generating self-signed SSL certificates..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=CA/L=San Francisco/O=AI Test Automation/CN=localhost"
        log_success "SSL certificates generated"
    fi
    
    # Create database initialization script
    cat > database/init.sql << 'EOF'
-- AI Test Automation Database Schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_quota INTEGER DEFAULT 100,
    api_usage INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test executions table
CREATE TABLE IF NOT EXISTS test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    progress FLOAT DEFAULT 0.0,
    current_phase VARCHAR(100),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER, -- seconds
    results JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test results table
CREATE TABLE IF NOT EXISTS test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES test_executions(id),
    test_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    duration FLOAT,
    error_message TEXT,
    screenshots JSONB,
    logs JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Requirements templates table
CREATE TABLE IF NOT EXISTS requirements_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    application_type VARCHAR(50) NOT NULL,
    template_config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default templates
INSERT INTO requirements_templates (name, display_name, description, application_type, template_config)
VALUES 
    ('ecommerce', 'E-commerce', 'Requirements template for e-commerce applications', 'ecommerce', '{}'),
    ('hrms', 'HRMS', 'Requirements template for HR management systems', 'enterprise_hrms', '{}'),
    ('banking', 'Banking', 'Requirements template for banking applications', 'financial_banking', '{}')
ON CONFLICT (name) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_test_executions_user_id ON test_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_test_executions_status ON test_executions(status);
CREATE INDEX IF NOT EXISTS idx_test_results_execution_id ON test_results(execution_id);
EOF
    
    log_success "Environment setup completed"
}

# Deploy with Docker Compose
deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."
    
    # Build images
    log_info "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "Up"; then
        log_success "Services are running"
        
        # Display service URLs
        echo ""
        log_success "🎉 Deployment completed successfully!"
        echo ""
        echo "📊 Service URLs:"
        echo "   Web Dashboard: http://localhost:3000"
        echo "   API Backend:   http://localhost:8000"
        echo "   API Docs:      http://localhost:8000/docs"
        echo "   Database:      localhost:5432"
        echo "   Redis:         localhost:6379"
        echo "   Grafana:       http://localhost:3001 (admin/admin123)"
        echo "   Prometheus:    http://localhost:9090"
        echo ""
        echo "🔐 Default Credentials:"
        echo "   Admin: admin / admin123"
        echo "   Demo:  demo / demo123"
        echo ""
    else
        log_error "Some services failed to start"
        docker-compose logs
        exit 1
    fi
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/deployment.yaml
    
    # Wait for deployments to be ready
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/postgres -n ai-test-automation
    kubectl wait --for=condition=available --timeout=300s deployment/redis -n ai-test-automation
    kubectl wait --for=condition=available --timeout=300s deployment/api-backend -n ai-test-automation
    kubectl wait --for=condition=available --timeout=300s deployment/web-dashboard -n ai-test-automation
    
    # Get service information
    log_success "🎉 Kubernetes deployment completed!"
    echo ""
    echo "📊 Service Information:"
    kubectl get services -n ai-test-automation
    echo ""
    echo "🌐 Ingress Information:"
    kubectl get ingress -n ai-test-automation
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    
    if [ "$DEPLOYMENT_TYPE" = "docker-compose" ]; then
        docker-compose down -v
        docker system prune -f
    elif [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        kubectl delete namespace ai-test-automation
    fi
    
    log_success "Cleanup completed"
}

# Main execution
main() {
    case "$1" in
        "docker-compose"|"")
            DEPLOYMENT_TYPE="docker-compose"
            check_prerequisites
            setup_environment
            deploy_docker_compose
            ;;
        "kubernetes"|"k8s")
            DEPLOYMENT_TYPE="kubernetes"
            check_prerequisites
            setup_environment
            deploy_kubernetes
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [deployment-type] [environment]"
            echo ""
            echo "Deployment Types:"
            echo "  docker-compose  Deploy using Docker Compose (default)"
            echo "  kubernetes      Deploy to Kubernetes cluster"
            echo "  cleanup         Clean up all resources"
            echo ""
            echo "Environments:"
            echo "  production      Production environment (default)"
            echo "  development     Development environment"
            echo ""
            echo "Examples:"
            echo "  $0                          # Deploy with Docker Compose"
            echo "  $0 kubernetes production    # Deploy to Kubernetes"
            echo "  $0 cleanup                  # Clean up resources"
            ;;
        *)
            log_error "Unknown deployment type: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
