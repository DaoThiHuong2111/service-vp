#!/bin/bash

# Multi-Service AI Deployment Script
# Deploys both chunk-text and embedding services

set -e

echo "🚀 Starting AI Services Deployment..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker and Docker Compose are installed
print_status "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Prerequisites check passed ✓"

# Stop existing containers if any
print_status "Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Build and start services
print_status "Building and starting AI services..."
docker-compose up -d --build

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
echo "This may take a few minutes as models need to be downloaded..."

# Function to check service health
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:$port/health > /dev/null 2>&1; then
            print_success "$service_name is ready on port $port ✓"
            return 0
        fi
        
        if [ $((attempt % 10)) -eq 0 ]; then
            print_status "Still waiting for $service_name... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    print_warning "$service_name health check timeout. Check logs with: docker-compose logs $service_name"
    return 1
}

# Check services
print_status "Checking chunk-text API..."
check_service "chunk-text-api" "8087"

print_status "Checking embedding API..." 
check_service "embedding-api" "8088"

# Show final status
echo ""
echo "🎉 Deployment completed!"
echo "======================="
echo ""
echo "📡 Services Status:"
echo "  • Chunk Text API: http://localhost:8087"
echo "  • Embedding API:  http://localhost:8088"
echo ""
echo "📊 Useful commands:"
echo "  • View logs:      docker-compose logs -f"
echo "  • Stop services:  docker-compose down"
echo "  • Restart:        docker-compose restart"
echo "  • Status:         docker-compose ps"
echo ""

# Show container status
print_status "Current container status:"
docker-compose ps 