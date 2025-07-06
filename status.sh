#!/bin/bash

# Status Check Script for AI Services
# Displays comprehensive status of all services

echo "📊 AI Services Status Dashboard"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running!"
    exit 1
fi

echo ""
print_status "Container Status:"
echo "=================="
docker-compose ps

echo ""
print_status "Service Health Checks:"
echo "======================="

# Check chunk-text API
if curl -f -s http://localhost:8087/health > /dev/null 2>&1; then
    print_success "✓ Chunk Text API (Port 8087) - HEALTHY"
    
    # Try to get API info if available
    if curl -f -s http://localhost:8087/docs > /dev/null 2>&1; then
        echo "  📖 API Documentation: http://localhost:8087/docs"
    fi
else
    print_error "✗ Chunk Text API (Port 8087) - UNHEALTHY"
fi

# Check embedding API
if curl -f -s http://localhost:8088/health > /dev/null 2>&1; then
    print_success "✓ Embedding API (Port 8088) - HEALTHY"
    
    # Try to get model info
    if curl -f -s http://localhost:8088/models > /dev/null 2>&1; then
        echo "  🤖 Models endpoint: http://localhost:8088/models"
    fi
else
    print_error "✗ Embedding API (Port 8088) - UNHEALTHY"
fi

echo ""
print_status "Resource Usage:"
echo "================"

# Check CPU and memory usage for our containers
if command -v docker stats --no-stream > /dev/null 2>&1; then
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" $(docker-compose ps -q) 2>/dev/null || echo "No containers running"
fi

echo ""
print_status "Network Information:"
echo "===================="
docker network ls --filter "name=vps" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"

echo ""
print_status "Volume Information:"
echo "==================="
docker volume ls --filter "name=vps\|infinity" --format "table {{.Name}}\t{{.Driver}}"

echo ""
print_status "Recent Logs (last 20 lines):"
echo "============================="
echo "Chunk Text API:"
docker-compose logs --tail=10 chunk-text-api 2>/dev/null || echo "No logs available"

echo ""
echo "Embedding API:"
docker-compose logs --tail=10 embedding-api 2>/dev/null || echo "No logs available"

echo ""
print_status "Quick Actions:"
echo "=============="
echo "• View live logs:     docker-compose logs -f"
echo "• Restart services:   docker-compose restart"
echo "• Stop services:      docker-compose down"
echo "• Cleanup:           ./cleanup.sh"
echo "• Full redeploy:     ./deploy.sh"

echo "" 