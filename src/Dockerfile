FROM ollama/ollama

# Argument to specify the model to be pulled during the build
ARG MODEL_NAME

# Set environment variables
ENV BUILT_IN_OLLAMA_MODEL=${MODEL_NAME}
ENV OLLAMA_HOST=0.0.0.0

# Install curl, which is used for healthcheck polling.
USER root
RUN apt-get clean && \
  for i in 1 2 3; do \
  apt-get update && apt-get install -y curl && break; \
  echo "apt-get failed, retrying in 5 seconds..."; \
  sleep 5; \
  done && \
  rm -rf /var/lib/apt/lists/*

# Pull the specified model into the image during the build process.
RUN set -eux; \
  ollama serve > /dev/null 2>&1 & \
  t=0; \
  until curl -sSf --max-time 2 http://127.0.0.1:11434 > /dev/null; do \
  if [ "$t" -ge 300 ]; then echo "Timeout waiting for ollama server"; exit 1; fi; \
  echo "Waiting for ollama server to start..."; \
  sleep 1; \
  t=$((t+1)); \
  done; \
  \
  # Pull the model if MODEL_NAME is provided
  if [ -n "${MODEL_NAME}" ]; then \
  echo "Pulling model: ${MODEL_NAME}"; \
  if ! ollama pull "${MODEL_NAME}"; then \
  echo "ERROR: Failed to pull model: ${MODEL_NAME}" >&2; \
  exit 1; \
  fi; \
  fi

# Copy the simplified entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Add a healthcheck to ensure the Ollama server is responsive
HEALTHCHECK --interval=10s --timeout=5s --start-period=300s --retries=30 \
  CMD curl -fsS http://127.0.0.1:11434 >/dev/null || exit 1

VOLUME ["/root/.ollama"]

ENTRYPOINT ["/entrypoint.sh"]
