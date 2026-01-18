#!/bin/bash
# setup_dev_env.sh
# ARC Secretariat Environment Setup Script
# Run this on each machine (iMac, MacBook Air) to build the local environment.

VENV_NAME="shared_venv"

echo "🛠️  ARC Secretariat Environment Setup"
echo "======================================"

# 1. Clean up broken environment
if [ -d "$VENV_NAME" ]; then
    echo "🗑️  Removing existing (possibly broken) $VENV_NAME..."
    rm -rf "$VENV_NAME"
fi

# 2. Create new venv
echo "📦 Creating new virtual environment: $VENV_NAME..."
python3 -m venv "$VENV_NAME"

# 3. Activate and Install
echo "🔌 Activating and installing dependencies..."
source "$VENV_NAME/bin/activate"

# Update pip
pip install --upgrade pip

# Install Critical Dependencies
pip install \
    requests \
    chromadb \
    sentence-transformers \
    playwright \
    langchain-text-splitters \
    tiktoken \
    pydantic-settings \
    PyYAML \
    google-genai

# Playwright install (optional check)
# playwright install chromium 

echo ""
echo "✅ Setup Complete!"
echo "👉 To use: source $VENV_NAME/bin/activate"
