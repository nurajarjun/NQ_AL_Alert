FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install pandas-ta WITHOUT upgrading numpy (critical for model compatibility)
# Use --no-deps to prevent dependency upgrades, then install only what's needed
RUN pip install --no-cache-dir --no-deps pandas-ta || echo "pandas-ta installation failed, continuing without it"
RUN pip install --no-cache-dir tqdm numba  # pandas-ta dependencies

# Copy entire project
COPY . .

# Create necessary directories
RUN mkdir -p ml/data ml/models backend/ml/models

# Expose port
EXPOSE 8001

# Set Python path to include current directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Run from project root (critical for imports)
CMD ["python", "backend/main.py"]
