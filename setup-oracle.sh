#!/bin/bash
# Automated Oracle Cloud Setup Script for NQ-AI-Alerts
# This script installs Docker, clones the repo, and sets up the environment

set -e  # Exit on any error

echo "🚀 Starting NQ-AI-Alerts Automated Setup..."
echo "================================================"

# Update system
echo "📦 Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt install -y docker.io

# Start and enable Docker
echo "▶️  Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
echo "✅ Verifying installations..."
docker --version
docker-compose --version

# Clone repository
echo "📥 Cloning NQ-AI-Alerts repository..."
cd ~
if [ -d "NQ_AL_Alert" ]; then
    echo "Repository already exists, pulling latest..."
    cd NQ_AL_Alert
    git pull origin main
else
    git clone https://github.com/nurajarjun/NQ_AL_Alert.git
    cd NQ_AL_Alert
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
# Telegram Configuration
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}

# AI API Keys
GEMINI_API_KEY=${GEMINI_API_KEY}
NEWS_API_KEY=${NEWS_API_KEY}

# Application Settings
AUTONOMOUS_MODE=true
ALERT_THRESHOLD=70
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
EOF
    echo "⚠️  NOTE: .env file created with placeholders. Update with actual values!"
else
    echo "✅ .env file already exists"
fi

# Build Docker image (this is the long part)
echo "🏗️  Building Docker image (this may take 10-15 minutes)..."
echo "📦 Installing Python libraries in background..."

# Build in background and send keep-alive signals
(
  while true; do
    echo "⏳ Still building... $(date +%H:%M:%S)"
    sleep 60
  done
) &
KEEPALIVE_PID=$!

# Build Docker image
sudo docker-compose build

# Stop keep-alive
kill $KEEPALIVE_PID 2>/dev/null || true

echo "✅ Docker build complete!"

# Start containers
echo "🚀 Starting containers..."
sudo docker-compose up -d

# Wait for startup (increased from 20 to 60 seconds)
echo "⏳ Waiting for services to start (60 seconds)..."
sleep 60

# Health check with retries
echo "🏥 Running health check..."
MAX_RETRIES=5
RETRY_COUNT=0
HEALTH_CHECK_PASSED=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8001/; then
        echo "✅ Health check passed!"
        HEALTH_CHECK_PASSED=true
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "⚠️  Health check failed (attempt $RETRY_COUNT/$MAX_RETRIES). Retrying in 10 seconds..."
            sleep 10
        fi
    fi
done

if [ "$HEALTH_CHECK_PASSED" = false ]; then
    echo "❌ Health check failed after $MAX_RETRIES attempts"
    echo "📋 Container logs:"
    sudo docker-compose logs --tail=50
    echo "⚠️  Containers are running but not responding. Check logs above."
fi

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "📋 Next Steps:"
echo "1. Update .env file with your actual API keys:"
echo "   nano ~/NQ_AL_Alert/.env"
echo ""
echo "2. Restart containers after updating .env:"
echo "   cd ~/NQ_AL_Alert && docker-compose restart"
echo ""
echo "3. View logs:"
echo "   cd ~/NQ_AL_Alert && docker-compose logs -f"
echo ""
echo "4. Check status:"
echo "   cd ~/NQ_AL_Alert && docker-compose ps"
echo ""
echo "🎉 Your NQ-AI-Alerts system is ready!"
