#!/bin/bash

# Job Market Intelligence Pipeline - Local Setup Script
# This script sets up everything needed to run the pipeline locally

set -e

echo "🚀 Starting Job Market Intelligence Pipeline Setup..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $PYTHON_VERSION"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "🔄 Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt -q
echo "   ✓ Dependencies installed"

# Check PostgreSQL
echo ""
echo "🗄️  Checking PostgreSQL installation..."
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL client not found${NC}"
    echo "   Install PostgreSQL:"n    echo "   macOS (Homebrew): brew install postgresql"
    echo "   Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "   Windows: Download from https://www.postgresql.org/download/windows/"
else
    PSQL_VERSION=$(psql --version)
    echo "   ✓ $PSQL_VERSION"
fi

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs data/raw data/processed airflow sql/tables sql/views
echo "   ✓ Directories created"

# Create .env if it doesn't exist
echo ""
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✓ .env created from .env.example"
    echo -e "${YELLOW}   ⚠️  Please edit .env with your database credentials${NC}"
else
    echo "   ✓ .env already exists"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo ""
echo "1️⃣  Edit .env with your database credentials:"
echo "   nano .env"
echo ""
echo "2️⃣  Start PostgreSQL:"
echo "   macOS: brew services start postgresql"
echo "   Linux: sudo systemctl start postgresql"
echo ""
echo "3️⃣  Create database and schema:"
echo "   python setup.py"
echo ""
echo "4️⃣  Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "5️⃣  Setup Airflow:"
echo "   bash setup_airflow.sh"
echo ""
echo "6️⃣  Start Airflow (two terminals):"
echo "   Terminal 1: airflow webserver"
echo "   Terminal 2: airflow scheduler"
echo ""
echo "7️⃣  Open browser:"
echo "   http://localhost:8080"
echo ""
