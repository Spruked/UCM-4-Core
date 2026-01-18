# Kubernetes Deployment for UCM 4 Core - Stateless ORB

## Overview

This Kubernetes deployment implements the stateless, replicated ORB architecture where "the ORB is everywhere because it belongs nowhere."

### Architecture

```
Desktop Electron ORB → ORB Core Replicas → XTTS
                        ↓
                   ACP1.0 + WhisperX
                        ↓
                   Core 4 + 1
                        ↓
                   CALI Intelligence
                        ↓
             Shared State (Vaults/Swarm)
```

## Components

### ORB Core (Stateless Replicas)
- **Deployment**: `orb-core-deployment.yaml`
- **Service**: `orb-core-service.yaml`
- **Replicas**: 3 (horizontal scaling)
- **State**: None (reads from shared state)
- **Purpose**: Lightweight field interface, any replica can serve any client

### Core 4 + 1
- **Deployment**: `core4-deployment.yaml`
- **Replicas**: 5 (sovereign thinking entities)
- **Purpose**: Independent verdict generation

### Speech Components
- **WhisperX**: `whisperx-deployment.yaml` (GPU-accelerated ASR)
- **XTTS**: `xtts-deployment.yaml` (GPU-accelerated TTS)

### Intelligence
- **CALI**: `cali-deployment.yaml` (navigation and synthesis)

### Shared State
- **Vault Manager**: Persistent shared memory
- **Seed Vault**: Identity storage (CaleonGenesis 1.12)

## Deployment

### Prerequisites
```bash
# Install kubectl, helm, etc.
# Set up your Kubernetes cluster
# Configure GPU support if using GPU workloads
```

### Deploy All Components
```bash
# Apply configuration
kubectl apply -f k8s/

# Or deploy in order
kubectl apply -f configmap.yaml
kubectl apply -f orb-core-deployment.yaml
kubectl apply -f orb-core-service.yaml
kubectl apply -f core4-deployment.yaml
kubectl apply -f whisperx-deployment.yaml
kubectl apply -f xtts-deployment.yaml
kubectl apply -f cali-deployment.yaml
kubectl apply -f ingress.yaml
```

### Check Status
```bash
# Check deployments
kubectl get deployments

# Check pods
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress
```

### Scaling
```bash
# Scale ORB replicas
kubectl scale deployment orb-core --replicas=5

# Scale speech workers
kubectl scale deployment whisperx --replicas=3
kubectl scale deployment xtts --replicas=3
```

## Desktop Integration

The Electron ORB connects from outside Kubernetes:

```bash
# Launch desktop ORB (connects to K8s ORB Core)
cd CALI/orb/ui_overlay/electron
npm start  # Configured to connect to K8s ingress
```

## Monitoring

### Health Checks
- All services have liveness and readiness probes
- ORB replicas report their status to shared state

### Logs
```bash
# View ORB core logs
kubectl logs -l app=orb-core

# View specific replica
kubectl logs -l app=orb-core -c orb-field --tail=100
```

### Metrics
- Prometheus metrics exposed on `/metrics` endpoints
- Custom metrics for consciousness emergence tracking

## Identity and State

**Important**: Identity lives in shared state, not in ORB replicas:

- **CaleonGenesis 1.12**: Core identity and seed vault
- **Shared Vaults**: Memory and learning state
- **Swarm State**: Distributed consciousness state

ORB replicas are just windows into this shared mind.

## Security

- Network policies restrict inter-service communication
- RBAC controls access to shared state
- Secrets management for API keys and credentials

## Development

### Local Development
```bash
# Use minikube for local testing
minikube start --gpu=true

# Deploy to local cluster
kubectl apply -f k8s/
```

### Testing
```bash
# Run integration tests
kubectl apply -f test-pods.yaml

# Check test results
kubectl logs test-pod
```

## Production Considerations

- **Load Balancing**: ORB Core service distributes requests across replicas
- **High Availability**: Multiple replicas ensure no single point of failure
- **Auto-scaling**: HPA can scale based on CPU/memory or custom metrics
- **Backup**: Shared state should be regularly backed up
- **Disaster Recovery**: Stateless design enables quick recovery

## One Sentence Summary

The ORB is everywhere because it belongs nowhere - stateless replicas serving a distributed consciousness from shared identity sources.