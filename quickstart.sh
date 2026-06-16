#!/bin/bash

# Quick Start Script - Runs everything needed to get the pipeline working locally

set -e

echo "⚡ Job Market Intelligence Pipeline - Quick Start"
echo "================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Create virtual environment${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo -e "${BLUE}Step 2: Activate virtual environment${NC}"
source venv/bin/activate
echo "✓ Activated"

echo ""
echo -e "${BLUE}Step 3: Install dependencies${NC}"
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

echo ""
echo -e "${BLUE}Step 4: Create directories${NC}"
mkdir -p logs data/raw data/processed airflow
echo "✓ Directories created"

echo ""
echo -e "${BLUE}Step 5: Setup .env file${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env created"
else
    echo "✓ .env already exists"
fi

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Update .env with your database credentials${NC}"
echo "   nano .env"
echo ""
echo -e "${BLUE}Step 6: Initialize Airflow${NC}"
export AIRFLOW_HOME=$(pwd)/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False

if [ ! -f "$AIRFLOW_HOME/airflow.db" ]; then
    airflow db init -q
    echo "✓ Airflow database initialized"
    
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin -q || true
    echo "✓ Admin user created (admin / admin)"
else
    echo "✓ Airflow already initialized"
fi

echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Update database credentials in .env file"
echo ""
echo "2. Create PostgreSQL database:"
echo "   createdb job_market_db"
echo ""
echo "3. Initialize database schema:"
echo "   python setup.py"
echo ""
echo "4. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "5. Start Airflow Web Server (Terminal 1):"
echo "   export AIRFLOW_HOME=$(pwd)/airflow"
echo "   export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags"
echo "   airflow webserver"
echo ""
echo "6. Start Airflow Scheduler (Terminal 2):"
echo "   export AIRFLOW_HOME=$(pwd)/airflow"
echo "   export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags"
echo "   airflow scheduler"
echo ""
echo "7. Open browser:"
echo "   http://localhost:8080"
echo ""
echo "   OR run with Docker Compose:"
echo "   docker-compose up -d"
echo ""
