#!/bin/bash

# Cleanup Script for AI Services
# Stops containers, removes images, and cleans up volumes

set -e

echo "🧹 AI Services Cleanup"
echo "====================="

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

# Parse command line arguments
CLEAN_ALL=false
CLEAN_VOLUMES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            CLEAN_ALL=true
            shift
            ;;
        --volumes)
            CLEAN_VOLUMES=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --all      Remove images and system cleanup"
            echo "  --volumes  Also remove volumes (model cache will be lost)"
            echo "  -h, --help Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Stop and remove containers
print_status "Stopping and removing containers..."
docker-compose down --remove-orphans

if [ "$CLEAN_VOLUMES" = true ]; then
    print_warning "Removing volumes (model cache will be lost)..."
    docker-compose down -v
    print_success "Volumes removed ✓"
fi

# Remove images if requested
if [ "$CLEAN_ALL" = true ]; then
    print_status "Removing AI service images..."
    
    # Remove chunk-text image
    if docker images | grep -q "vps_chunk-text-api\|vps-chunk-text-api"; then
        docker rmi $(docker images --format "table {{.Repository}}:{{.Tag}}" | grep "vps.*chunk-text-api" | head -1) 2>/dev/null || true
        print_success "Chunk-text image removed ✓"
    fi
    
    # Remove embedding image (optional - it's a public image)
    if docker images | grep -q "michaelf34/infinity"; then
        read -p "Remove embedding image (michaelf34/infinity)? This will require re-download [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker rmi michaelf34/infinity:latest 2>/dev/null || true
            print_success "Embedding image removed ✓"
        fi
    fi
    
    # Docker system cleanup
    print_status "Running Docker system cleanup..."
    docker system prune -f
    print_success "Docker system cleanup completed ✓"
fi

# Show remaining containers and images
echo ""
print_status "Remaining AI-related containers:"
docker ps -a --filter "name=chunk-text\|embedding" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "No AI containers found"

echo ""
print_status "Remaining AI-related images:"
docker images --filter "reference=vps*" --filter "reference=michaelf34/infinity" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" || echo "No AI images found"

echo ""
print_success "Cleanup completed! 🎉"
echo ""
echo "To redeploy services, run: ./deploy.sh" 