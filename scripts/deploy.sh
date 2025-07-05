#!/bin/bash

# ThirdPartyRiskPortal Deployment Script
# This script automates the deployment of the TPRM application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        warn ".env file not found. Creating from template..."
        cp .env.example .env 2>/dev/null || {
            error "No .env.example found. Please create a .env file with required environment variables."
        }
    fi
    
    log "Prerequisites check completed successfully."
}

# Setup environment
setup_environment() {
    log "Setting up environment: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        "development")
            export COMPOSE_PROJECT_NAME=tprm-dev
            ;;
        "staging")
            export COMPOSE_PROJECT_NAME=tprm-staging
            ;;
        "production")
            export COMPOSE_PROJECT_NAME=tprm-prod
            ;;
        *)
            error "Invalid environment. Use: development, staging, or production"
            ;;
    esac
    
    log "Environment setup completed."
}

# Build images
build_images() {
    log "Building Docker images..."
    
    # Build backend
    log "Building backend image..."
    docker-compose -f $DOCKER_COMPOSE_FILE build backend
    
    # Build frontend
    log "Building frontend image..."
    docker-compose -f $DOCKER_COMPOSE_FILE build frontend
    
    log "Image building completed."
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start core services first
    log "Starting database and Redis..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d postgres redis
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    sleep 10
    
    # Start backend
    log "Starting backend service..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d backend
    
    # Wait for backend to be ready
    log "Waiting for backend to be ready..."
    sleep 15
    
    # Start frontend
    log "Starting frontend service..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d frontend
    
    # Start additional services
    log "Starting additional services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d zipkin nginx
    
    log "Services started successfully."
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Check backend health
    log "Checking backend health..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health &>/dev/null; then
            log "Backend is healthy."
            break
        fi
        if [ $i -eq 30 ]; then
            error "Backend health check failed after 30 attempts."
        fi
        sleep 2
    done
    
    # Check frontend health
    log "Checking frontend health..."
    for i in {1..30}; do
        if curl -f http://localhost:3000 &>/dev/null; then
            log "Frontend is healthy."
            break
        fi
        if [ $i -eq 30 ]; then
            error "Frontend health check failed after 30 attempts."
        fi
        sleep 2
    done
    
    log "All health checks passed."
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    # Run database migrations
    log "Running database migrations..."
    docker-compose -f $DOCKER_COMPOSE_FILE exec backend python -m alembic upgrade head
    
    # Create initial data if needed
    if [ "$ENVIRONMENT" = "development" ]; then
        log "Creating initial development data..."
        docker-compose -f $DOCKER_COMPOSE_FILE exec backend python -c "
from app.database import SessionLocal
from app.models import User
from app.security import get_password_hash

db = SessionLocal()
try:
    # Create admin user if not exists
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@tprm.com',
            full_name='System Administrator',
            hashed_password=get_password_hash('admin123'),
            role='ADMIN',
            is_active=True
        )
        db.add(admin)
        db.commit()
        print('Admin user created successfully')
    else:
        print('Admin user already exists')
finally:
    db.close()
"
    fi
    
    log "Database setup completed."
}

# Show status
show_status() {
    log "Application Status:"
    echo ""
    echo "Services:"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    echo ""
    echo "Access URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Health Check: http://localhost:8000/health"
    echo "  Zipkin Tracing: http://localhost:9411"
    echo ""
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "Development Credentials:"
        echo "  Username: admin"
        echo "  Password: admin123"
        echo ""
    fi
}

# Stop services
stop_services() {
    log "Stopping services..."
    docker-compose -f $DOCKER_COMPOSE_FILE down
    log "Services stopped."
}

# Clean up
cleanup() {
    log "Cleaning up..."
    docker-compose -f $DOCKER_COMPOSE_FILE down -v --remove-orphans
    docker system prune -f
    log "Cleanup completed."
}

# Main deployment function
deploy() {
    log "Starting TPRM deployment for environment: $ENVIRONMENT"
    
    check_prerequisites
    setup_environment
    build_images
    start_services
    health_check
    setup_database
    show_status
    
    log "Deployment completed successfully!"
}

# Main script logic
case "${2:-deploy}" in
    "deploy")
        deploy
        ;;
    "start")
        start_services
        health_check
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        health_check
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "logs")
        docker-compose -f $DOCKER_COMPOSE_FILE logs -f
        ;;
    "status")
        docker-compose -f $DOCKER_COMPOSE_FILE ps
        ;;
    *)
        echo "Usage: $0 {environment} {command}"
        echo ""
        echo "Environments:"
        echo "  development  - Development environment"
        echo "  staging      - Staging environment"
        echo "  production   - Production environment"
        echo ""
        echo "Commands:"
        echo "  deploy       - Full deployment (default)"
        echo "  start        - Start services"
        echo "  stop         - Stop services"
        echo "  restart      - Restart services"
        echo "  cleanup      - Clean up all containers and volumes"
        echo "  logs         - Show service logs"
        echo "  status       - Show service status"
        echo ""
        echo "Examples:"
        echo "  $0 development deploy"
        echo "  $0 production start"
        echo "  $0 development logs"
        exit 1
        ;;
esac 