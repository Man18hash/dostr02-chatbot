#!/bin/bash

# DOST Hybrid Chatbot Deployment Script
# For Ubuntu 24.04 LTS

echo "🚀 Starting DOST Hybrid Chatbot Deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed"
fi

# Start Docker service
echo "🔄 Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Clone or update repository
echo "📥 Setting up application..."
if [ ! -d "dost-hybrid-chatbot" ]; then
    git clone https://github.com/Man18hash/dostr02-chatbot.git dost-hybrid-chatbot
else
    cd dost-hybrid-chatbot
    git pull
fi

cd dost-hybrid-chatbot

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data storage

# Build and run with Docker Compose
echo "🏗️ Building and starting container..."
sudo docker-compose up --build -d

# Wait for service to be ready
echo "⏳ Waiting for service to start..."
sleep 30

# Check if service is running
if sudo docker-compose ps | grep -q "Up"; then
    echo "✅ DOST Hybrid Chatbot is running!"
    echo "🌐 Local access: http://localhost:7860"
    echo ""
    echo "🔍 To get your public IP:"
    echo "   curl ifconfig.me"
    echo ""
    echo "🌍 Public access will be: http://YOUR_PUBLIC_IP:7860"
    echo ""
    echo "📝 To check logs: sudo docker-compose logs -f"
    echo "🛑 To stop: sudo docker-compose down"
else
    echo "❌ Failed to start service. Check logs:"
    sudo docker-compose logs
fi
