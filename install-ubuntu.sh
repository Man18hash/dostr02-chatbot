#!/bin/bash

echo "🐧 Installing DOST Hybrid Chatbot on Ubuntu Desktop..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python..."
sudo apt install -y python3 python3-pip python3-venv

# Install system dependencies for ML models
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    build-essential \
    curl \
    git \
    libsndfile1 \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0

# Create virtual environment
echo "📁 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📂 Creating directories..."
mkdir -p data storage

echo "✅ Installation complete!"
echo ""
echo "🚀 To run the chatbot:"
echo "   source .venv/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 The chatbot will be available at: http://localhost:7860"
