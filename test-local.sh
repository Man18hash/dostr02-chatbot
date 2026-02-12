#!/bin/bash

echo "🧪 Testing DOST Hybrid Chatbot Locally..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Starting Docker..."
    open -a Docker || echo "Please start Docker Desktop manually"
    sleep 5
fi

# Stop any existing container
echo "🛑 Stopping existing containers..."
docker stop test-chatbot 2>/dev/null || true
docker rm test-chatbot 2>/dev/null || true

# Build and run
echo "🏗️ Building and running test container..."
docker build -t dost-chatbot .
docker run -d \
    --name test-chatbot \
    -p 7860:7860 \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/storage:/app/storage" \
    dost-chatbot

# Wait for startup
echo "⏳ Waiting for chatbot to start..."
sleep 10

# Check if running
if docker ps | grep -q test-chatbot; then
    echo "✅ Chatbot is running!"
    echo "🌐 Open: http://localhost:7860"
    echo ""
    echo "📊 View logs: docker logs -f test-chatbot"
    echo "🛑 Stop test: docker stop test-chatbot"
    
    # Try to open browser
    if command -v open; then
        open http://localhost:7860
    elif command -v xdg-open; then
        xdg-open http://localhost:7860
    else
        echo "Manually open: http://localhost:7860"
    fi
else
    echo "❌ Failed to start. Checking logs..."
    docker logs test-chatbot
fi
