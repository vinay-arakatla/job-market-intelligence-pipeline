# Job Market Intelligence Pipeline - Development Setup

All commands assume you're in the project root directory.

## Local Development Setup

### 1. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create database (macOS with Homebrew PostgreSQL)
creatdb job_market_db

# Or using psql
psql -U postgres
# Then in psql:
create database job_market_db;

# Setup schema
python setup.py
```

### 3. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Pipeline Manually
```bash
# Extract jobs
python -m src.extract.jobspy_extractor

# Test scoring
python -m src.scoring.score_calculator

# Run tests
pytest tests/ -v
```

## Docker Compose Setup

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Initialize Airflow
```bash
docker-compose exec airflow airflow db init
docker-compose exec airflow airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin
```

### 3. Access Services
- Airflow Web UI: http://localhost:8080
- PostgreSQL: localhost:5432

### 4. Stop Services
```bash
docker-compose down
```

## Apache Airflow Setup (Manual)

### 1. Initialize Airflow
```bash
export AIRFLOW_HOME=$(pwd)/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False

airflow db init
```

### 2. Create Admin User
```bash
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
```

### 3. Start Services
```bash
# Terminal 1: Webserver
airflow webserver

# Terminal 2: Scheduler
airflow scheduler
```

### 4. Access Airflow
Open http://localhost:8080 in your browser

## Common Development Tasks

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_scorer.py -v

# With coverage
pytest --cov=src tests/
```

### Check Code
```bash
# Lint
pylint src/

# Format
black src/ tests/

# Type check
mypy src/
```

### Query Database
```bash
# Connect to PostgreSQL
psql -d job_market_db

# View tables
\dt

# View views
\dv

# Run query
SELECT * FROM vw_jobs_overview;
```

### Extract Data Manually
```python
from src.extract.jobspy_extractor import JobSpyExtractor

extractor = JobSpyExtractor()
jobs = extractor.extract_jobs(
    job_titles=['Data Analyst'],
    locations=['Berlin'],
    platforms=['linkedin']
)
print(f"Extracted {len(jobs)} jobs")
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Test connection
psql -h localhost -U job_user -d job_market_db

# Reset database
dropdb job_market_db
createdb job_market_db
python setup.py
```

### Airflow DAG Not Showing
```bash
# Check DAG syntax
airflow dags list
airflow dags validate

# Refresh
airflow dags list --reload
```

## IDE Setup

### VSCode
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### PyCharm
1. File → Settings → Project → Python Interpreter
2. Click gear → Add
3. Select "Existing environment"
4. Point to `venv/bin/python`

## Performance Optimization

### Database Indexes
All tables have indexes on commonly queried columns. Check `sql/tables/` for index definitions.

### Query Optimization
- Use views for complex queries
- Filter by date ranges when querying large tables
- Limit results with LIMIT clause

### Airflow Optimization
- Adjust `SCRAPE_BATCH_SIZE` in `.env`
- Use `max_active_runs` to limit parallel executions
- Monitor via Airflow Web UI
