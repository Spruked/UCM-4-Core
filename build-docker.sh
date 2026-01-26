#!/bin/bash
# UCM_4_Core Docker Build and Deploy Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="ucm-4-core"
TAG="latest"
REGISTRY=""  # Add your registry here if needed

echo -e "${BLUE}🚀 Building UCM_4_Core Docker Images${NC}"

# Build the main application image
echo -e "${YELLOW}Building main application image...${NC}"
docker build -t ${IMAGE_NAME}:${TAG} .

# Build individual core images
echo -e "${YELLOW}Building Caleon Genesis image...${NC}"
docker build -t ${IMAGE_NAME}-caleon:${TAG} ./Caleon_Genesis_1_12

echo -e "${YELLOW}Building Cali X One image...${NC}"
docker build -t ${IMAGE_NAME}-cali:${TAG} ./Cali_X_One

echo -e "${GREEN}✅ All images built successfully!${NC}"

# Tag images for registry if specified
if [ -n "$REGISTRY" ]; then
    echo -e "${YELLOW}Tagging images for registry...${NC}"
    docker tag ${IMAGE_NAME}:${TAG} ${REGISTRY}/${IMAGE_NAME}:${TAG}
    docker tag ${IMAGE_NAME}-caleon:${TAG} ${REGISTRY}/${IMAGE_NAME}-caleon:${TAG}
    docker tag ${IMAGE_NAME}-cali:${TAG} ${REGISTRY}/${IMAGE_NAME}-cali:${TAG}
fi

echo -e "${BLUE}🐳 Docker Images Created:${NC}"
echo "  - ${IMAGE_NAME}:${TAG}"
echo "  - ${IMAGE_NAME}-caleon:${TAG}"
echo "  - ${IMAGE_NAME}-cali:${TAG}"

echo -e "${GREEN}🎯 To run the application:${NC}"
echo "  docker-compose up -d"

echo -e "${GREEN}📊 To check status:${NC}"
echo "  docker-compose ps"
echo "  docker-compose logs -f"