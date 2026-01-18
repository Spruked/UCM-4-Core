#!/bin/bash
# UCM_4_Core/deploy_wsl.sh
# Deploy ORB system in WSL environment with Docker and Kubernetes

set -e

echo "🚀 Deploying UCM 4 Core ORB System in WSL"
echo "=========================================="

# Check if we're in WSL
if [ -z "$WSL_DISTRO_NAME" ]; then
    echo "❌ This script should be run in WSL environment"
    exit 1
fi

# Check Docker
echo "📦 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please restart WSL and run this script again."
    exit 0
fi

# Start Docker daemon if not running
sudo service docker start 2>/dev/null || true

# Check Kubernetes (k3s for lightweight deployment)
echo "☸️  Checking Kubernetes..."
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Installing k3s (lightweight Kubernetes)..."
    curl -sfL https://get.k3s.io | sh -
    sudo cp /usr/local/bin/k3s /usr/local/bin/kubectl
    mkdir -p ~/.kube
    sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
    sudo chown $(id -u):$(id -g) ~/.kube/config
    echo "✅ k3s installed"
fi

# Build Docker images
echo "🏗️  Building Docker images..."

# ORB Core image
cat > Dockerfile.orb << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Run ORB
CMD ["python", "orb_perception_integration.py"]
EOF

# Build the image
docker build -f Dockerfile.orb -t ucm4-orb:latest .

# Deploy to Kubernetes
echo "☸️  Deploying to Kubernetes..."

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/core4-deployment.yaml
kubectl apply -f k8s/whisperx-deployment.yaml
kubectl apply -f k8s/xtts-deployment.yaml
kubectl apply -f k8s/cali-deployment.yaml
kubectl apply -f k8s/orb-core-deployment.yaml
kubectl apply -f k8s/orb-core-service.yaml
kubectl apply -f k8s/ingress.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment --all

# Check status
echo "📊 Deployment Status:"
kubectl get pods
kubectl get services
kubectl get ingress

echo ""
echo "🎉 ORB System deployed successfully!"
echo ""
echo "Access points:"
echo "- ORB Core Service: kubectl port-forward svc/orb-core-service 8000:8000"
echo "- Check logs: kubectl logs -f deployment/orb-core-deployment"
echo ""
echo "Next steps:"
echo "1. Test the ORB: curl http://localhost:8000/health"
echo "2. Scale replicas: kubectl scale deployment orb-core-deployment --replicas=5"
echo "3. Monitor: kubectl top pods"