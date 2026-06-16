#!/bin/bash

# Airflow Setup Script
# Sets up Apache Airflow for the Job Market Intelligence Pipeline

set -e

echo "🚀 Setting up Apache Airflow..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Set Airflow environment variables
export AIRFLOW_HOME=$(pwd)/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__UNIT_TEST_MODE=True

echo "📁 Setting up Airflow directories..."
mkdir -p $AIRFLOW_HOME/logs
mkdir -p $AIRFLOW_HOME/plugins

echo "🔧 Initializing Airflow database..."
airflow db init

echo ""
echo "👤 Creating admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || echo "   ⚠️  User may already exist"

echo ""
echo -e "${GREEN}✅ Airflow setup complete!${NC}"
echo ""
echo "📝 To start Airflow, run in two separate terminals:"
echo ""
echo "Terminal 1 (Webserver):"
echo "   export AIRFLOW_HOME=$(pwd)/airflow"
echo "   export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags"
echo "   airflow webserver"
echo ""
echo "Terminal 2 (Scheduler):"
echo "   export AIRFLOW_HOME=$(pwd)/airflow"
echo "   export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags"
echo "   airflow scheduler"
echo ""
echo "🌐 Then open: http://localhost:8080"
echo "   Login: admin / admin"
echo ""
