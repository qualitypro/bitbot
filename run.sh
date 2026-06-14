#!/bin/bash

echo "🚀 Starting BitBot setup..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check config files
if [ ! -f "config.json" ]; then
    echo "⚠️ config.json not found. Creating from example..."
    cp config.example.json config.json
fi

if [ ! -f ".env" ]; then
    echo "⚠️ .env not found. Creating from example..."
    cp env.example .env
    echo "👉 Please edit .env with your API keys before running again."
    exit 1
fi

echo "✅ Setup complete. Launching BitBot..."

# Run the bot
python main.py