# Job Market Intelligence Pipeline

An automated data pipeline for scraping, analyzing, and scoring job postings from multiple platforms. Designed to help job seekers identify the most relevant opportunities based on their profile, skills, and preferences.

## 🎯 Features

- **Multi-platform Job Scraping**: Extract jobs from LinkedIn, Indeed, Glassdoor, and Google using JobSpy
- **Intelligent Job Scoring**: Calculate relevance scores (0-100) based on:
  - Skill match (40% weight)
  - Job title relevance (15%)
  - Seniority level fit (15%)
  - Location preference (15%)
  - German language requirement (10%)
  - Experience requirement (5%)
- **Data Quality Validation**: 7-point validation framework
- **Skill Extraction**: Automatic skill detection from job descriptions
- **Job Deduplication**: Identify and remove duplicate postings
- **Application Tracking**: Manual tracking of applications and their status
- **Power BI Dashboard Ready**: Pre-built SQL views for visualization
- **Automated Pipeline**: Apache Airflow DAG for daily scheduled execution

## 📊 Architecture

```
┌─────────────────┐
│   JobSpy API    │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐
│ Extract (extract/)      │ → raw_job_postings table
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│ Transform (transform/)  │ → cleaned_job_postings table
│ - Clean titles/company  │
│ - Parse location        │
│ - Detect remote type    │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│ Scoring (scoring/)      │ → job_match_scores table
│ - Extract skills        │ → job_skills table
│ - Calculate score       │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│ Quality (quality/)      │
│ - Validate data         │
└────────┬────────────────┘
         │
         ↓
┌──────────────────────────────┐
│ Dashboard Views & Reports    │
│ (Ready for Power BI/Tableau) │
└──────────────────────────────┘
```

## 🗄️ Database Schema

### Tables
- **raw_job_postings**: Landing zone for all scraped job data
- **cleaned_job_postings**: Cleaned and standardized job data
- **job_skills**: Extracted skills per job
- **job_match_scores**: Relevance scores and analysis
- **applications_tracker**: Manual application tracking

### Views
- `vw_jobs_overview`: Dashboard summary statistics
- `vw_top_hiring_companies`: Top hiring companies
- `vw_skills_demand`: Most in-demand skills
- `vw_jobs_by_location`: Geographic distribution
- `vw_high_priority_jobs`: Jobs with score 80+
- `vw_application_status_summary`: Application status breakdown
- `vw_jobs_by_posted_date`: Posting trends
- `vw_match_score_distribution`: Score distribution analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Apache Airflow 2.0+
- Git

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/vinay-arakatla/job-market-intelligence-pipeline.git
   cd job-market-intelligence-pipeline
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Create database and tables**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres -d job_market_db
   
   # Run schema scripts
   \i sql/tables/raw_job_postings.sql
   \i sql/tables/cleaned_job_postings.sql
   \i sql/tables/job_skills.sql
   \i sql/tables/job_match_scores.sql
   \i sql/tables/applications_tracker.sql
   \i sql/views/dashboard_views.sql
   ```

6. **Setup Airflow**
   ```bash
   export AIRFLOW_HOME=$(pwd)/airflow
   airflow db init
   airflow users create \
     --username admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com
   airflow webserver
   # In another terminal: airflow scheduler
   ```

## 📋 Configuration

Edit `.env` file to customize:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_market_db
DB_USER=your_username
DB_PASSWORD=your_password

# Job Search
JOB_TITLES=Data Analyst,BI Analyst,Junior Data Engineer,SQL Developer
JOB_LOCATIONS=Berlin,Germany
JOB_PLATFORMS=linkedin,indeed,glassdoor,google

# Your Profile
PROFILE_SKILLS=SQL,Python,Apache Airflow,PostgreSQL,Power BI,Tableau,ETL
GERMAN_LEVEL=B1
YEARS_EXPERIENCE=3

# Pipeline
PIPELINE_RUN_INTERVAL_DAYS=1
```

## 🏃 Usage

### Run Pipeline Manually
```python
from src.extract.jobspy_extractor import JobSpyExtractor
from src.load.db_loader import DatabaseLoader
from src.transform.data_cleaner import DataCleaner
from src.scoring.skill_extractor import extract_skills_for_jobs
from src.scoring.score_calculator import score_jobs_from_dataframe
from src.quality.data_validator import validate_dataframe

# Extract
extractor = JobSpyExtractor()
jobs_df = extractor.extract_jobs()

# Load raw
loader = DatabaseLoader()
loader.connect()
inserted, skipped = loader.load_raw_jobs(jobs_df)

# Clean
cleaner = DataCleaner()
cleaned_df = cleaner.clean_dataframe(jobs_df)

# Extract skills
skills_df = extract_skills_for_jobs(cleaned_df)

# Score
scored_df = score_jobs_from_dataframe(skills_df)

# Validate
validated_df, report = validate_dataframe(scored_df)
```

### Query Results
```python
from src.utils.database import get_psycopg2_connection

conn = get_psycopg2_connection()

# Get high priority jobs
query = "SELECT * FROM vw_high_priority_jobs ORDER BY match_score DESC LIMIT 10"
import pandas as pd
results = pd.read_sql_query(query, conn)
print(results)
```

## 📊 Scoring Logic

### Score Components

| Component | Weight | Details |
|-----------|--------|----------|
| **Skills Match** | 40% | Each matched skill = +5 points (max 10 = 50 pts) |
| **Job Title** | 15% | +10 for target roles (Data Analyst, BI Analyst, etc.) |
| **Seniority** | 15% | +20 Junior/Entry, +10 Mid-level, -10 Senior |
| **Location** | 15% | +15 Hybrid Berlin, +12 On-site Berlin, +10 Remote |
| **German** | 10% | +10 no requirement, +5 meets, -30 C1/C2 needed |
| **Experience** | 5% | +10 perfect fit, 0-5 close, -20 major gap |

### Priority Levels
- **High**: Score ≥ 80 → Focus applications here
- **Medium**: Score 50-79 → Consider these
- **Low**: Score < 50 → Review if desperate

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_scorer.py -v

# Run with coverage
pytest --cov=src tests/
```

## 📈 Power BI Integration

1. Connect Power BI to PostgreSQL database
2. Import views:
   - vw_jobs_overview
   - vw_top_hiring_companies
   - vw_skills_demand
   - vw_jobs_by_location
   - vw_high_priority_jobs
   - vw_match_score_distribution
3. Create visualizations:
   - KPI cards for summary stats
   - Stacked bar chart for priority distribution
   - Map visualization for geographic distribution
   - Line chart for posting trends
   - Table for high-priority jobs

## 🔍 Monitoring & Logging

- Logs stored in `logs/pipeline.log`
- Rotation: 10MB per file, 5 backups
- Log level configurable via `.env` (default: INFO)
- Airflow UI available at `http://localhost:8080`

## 📝 Project Structure

```
.
├── src/
│   ├── extract/          # JobSpy extractor
│   ├── load/             # Database loader
│   ├── transform/        # Data cleaning
│   ├── scoring/          # Skill extraction & scoring
│   ├── quality/          # Data validation
│   └── utils/            # Config, logging, database utilities
├── dags/                 # Airflow DAGs
├── sql/
│   ├── tables/           # Table schemas
│   └── views/            # Dashboard views
├── tests/                # Test suite
├── data/                 # Data directory (gitignored)
├── logs/                 # Log files (gitignored)
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## 🛠️ Troubleshooting

### No jobs scraped
- Check internet connection
- Verify job titles and locations in `.env`
- Check JobSpy timeout settings
- Some platforms may have rate limiting

### Database connection errors
- Verify PostgreSQL is running
- Check credentials in `.env`
- Ensure database exists: `createdb job_market_db`

### Airflow DAG not running
- Check Airflow scheduler is running
- Verify DAG syntax: `airflow dags list`
- Check logs: `airflow dags test job_market_intelligence_pipeline`

### Low match scores for relevant jobs
- Review scoring weights in `score_calculator.py`
- Check if skills are in `SKILL_CATEGORIES` in `skill_extractor.py`
- Update `.env` with your actual skills

## 📚 Technologies

- **Python 3.9+** - Core language
- **PostgreSQL** - Data warehouse
- **Apache Airflow** - Orchestration
- **JobSpy** - Job scraping
- **Pandas** - Data processing
- **SQLAlchemy** - ORM
- **psycopg2** - PostgreSQL adapter
- **pytest** - Testing framework

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👤 Author

**Vinay Arakatla**
- Email: vinayarakatla@gmail.com
- GitHub: [@vinay-arakatla](https://github.com/vinay-arakatla)

## 🙏 Acknowledgments

- JobSpy library for job scraping
- Apache Airflow for orchestration
- PostgreSQL community
- Open source contributors

## 📞 Support

For issues, questions, or suggestions:
1. Check existing [GitHub Issues](https://github.com/vinay-arakatla/job-market-intelligence-pipeline/issues)
2. Create new issue with detailed description
3. Include error logs and `.env` configuration (sanitized)

---

**Last Updated**: June 2026
