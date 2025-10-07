#!/usr/bin/env bash
set -euo pipefail

# Set default environment variables
export OLLAMA_HOST=${OLLAMA_HOST:-0.0.0.0:11434}
export OLLAMA_CONTEXT_LENGTH=${OLLAMA_CONTEXT_LENGTH:-4096}
export OLLAMA_MAX_LOADED_MODELS=${OLLAMA_MAX_LOADED_MODELS:-1}
export OLLAMA_NUM_PARALLEL=${OLLAMA_NUM_PARALLEL:-1}
export OLLAMA_MAX_QUEUE=${OLLAMA_MAX_QUEUE:-512}
export OLLAMA_FLASH_ATTENTION=${OLLAMA_FLASH_ATTENTION:-true}
export OLLAMA_KEEP_ALIVE=${OLLAMA_KEEP_ALIVE:-10m}
export OLLAMA_GPU_OVERHEAD=${OLLAMA_GPU_OVERHEAD:-1024}
export OLLAMA_KV_CACHE_TYPE=${OLLAMA_KV_CACHE_TYPE:-q8_0}

# Start ollama serve in the foreground
echo "Starting ollama serve on ${OLLAMA_HOST}..."
ollama serve
