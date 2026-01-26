# UCM_4_Core Dockerfile
# Multi-stage build for the Unified Consciousness Matrix Core 4 system

# Base stage with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libsndfile1 \
    libsndfile1-dev \
    portaudio19-dev \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for any frontend components (if needed)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Python stage
FROM base as python-deps

WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY Caleon_Genesis_1_12/requirements.txt Caleon_Genesis_1_12_requirements.txt
COPY Cali_X_One/requirements.txt Cali_X_One_requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r Caleon_Genesis_1_12_requirements.txt && \
    pip install -r Cali_X_One_requirements.txt

# Install PyTorch with CUDA support (if GPU available)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install additional ML dependencies
RUN pip install transformers accelerate tokenizers && \
    pip install TTS openai-whisper whisperx && \
    pip install torch-geometric

# Final application stage
FROM python-deps as app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Copy application code
COPY --chown=app:app . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/models

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose ports (adjust based on your services)
EXPOSE 8000 8080 3000

# Default command - can be overridden in docker-compose
CMD ["python", "start_ucm_core.py"]