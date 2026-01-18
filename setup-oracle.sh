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

# Build Docker image
echo "🏗️  Building Docker image..."
sudo docker-compose build

# Start containers
echo "🚀 Starting containers..."
sudo docker-compose up -d

# Wait for startup
echo "⏳ Waiting for services to start..."
sleep 15

# Health check
echo "🏥 Running health check..."
if curl -f http://localhost:8001/; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed, but containers are running. Check logs with: docker-compose logs"
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
