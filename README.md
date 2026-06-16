# Job Market Intelligence Pipeline

An automated job market intelligence and application tracking system using JobSpy, PostgreSQL, Apache Airflow, and Power BI. This system scrapes job postings, cleans data, calculates relevance scores based on your profile, and prepares data for visualization.

## 🎯 Objective

Build an end-to-end data engineering pipeline that:
- Scrapes job postings from multiple platforms (LinkedIn, Indeed, Glassdoor, Google Jobs)
- Stores raw and cleaned data in PostgreSQL
- Extracts skills and calculates job relevance scores
- Tracks job applications manually
- Provides data-ready views for Power BI dashboards

## 🛠 Tech Stack

- **Python 3.9+** - Main programming language
- **JobSpy** - Job scraping library
- **PostgreSQL** - Data warehouse
- **Apache Airflow** - Workflow orchestration
- **Pandas** - Data manipulation and analysis
- **SQLAlchemy/psycopg2** - Database connectivity
- **Power BI** - Data visualization and dashboards

## 📊 Project Structure

```
job-market-intelligence-pipeline/
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── setup.py                       # Package setup
├── dags/                          # Airflow DAG definitions
│   ├── __init__.py
│   └── job_pipeline_dag.py       # Main ETL DAG
├── src/                           # Source code
│   ├── __init__.py
│   ├── extract/                   # Data extraction
│   │   ├── __init__.py
│   │   └── jobspy_extractor.py   # JobSpy integration
│   ├── load/                      # Data loading
│   │   ├── __init__.py
│   │   └── db_loader.py          # PostgreSQL loader
│   ├── transform/                 # Data transformation
│   │   ├── __init__.py
│   │   └── data_cleaner.py       # Data cleaning logic
│   ├── scoring/                   # Job relevance scoring
│   │   ├── __init__.py
│   │   ├── skill_extractor.py    # Skill extraction
│   │   └── score_calculator.py   # Scoring logic
│   ├── quality/                   # Data quality checks
│   │   ├── __init__.py
│   │   └── data_validator.py     # Validation rules
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── config.py              # Configuration management
│       ├── logger.py              # Logging setup
│       └── database.py            # Database utilities
├── sql/                           # SQL scripts
│   ├── tables/                    # Table definitions
│   │   ├── raw_job_postings.sql
│   │   ├── cleaned_job_postings.sql
│   │   ├── job_skills.sql
│   │   ├── job_match_scores.sql
│   │   └── applications_tracker.sql
│   └── views/                     # Dashboard views
│       ├── vw_jobs_overview.sql
│       ├── vw_top_hiring_companies.sql
│       ├── vw_skills_demand.sql
│       ├── vw_jobs_by_location.sql
│       ├── vw_high_priority_jobs.sql
│       ├── vw_application_status_summary.sql
│       └── vw_jobs_by_posted_date.sql
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_extractor.py
│   ├── test_cleaner.py
│   └── test_scorer.py
└── data/                          # Data storage (gitignored)
    ├── raw/
    └── processed/
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- Apache Airflow 2.0 or higher
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/vinay-arakatla/job-market-intelligence-pipeline.git
cd job-market-intelligence-pipeline
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Initialize PostgreSQL database**
```bash
# Create database
createdb job_market_db

# Run table creation scripts
psql -U your_username -d job_market_db -f sql/tables/raw_job_postings.sql
psql -U your_username -d job_market_db -f sql/tables/cleaned_job_postings.sql
psql -U your_username -d job_market_db -f sql/tables/job_skills.sql
psql -U your_username -d job_market_db -f sql/tables/job_match_scores.sql
psql -U your_username -d job_market_db -f sql/tables/applications_tracker.sql

# Create views
psql -U your_username -d job_market_db -f sql/views/vw_jobs_overview.sql
# ... run all view files
```

6. **Initialize Airflow**
```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

7. **Start Airflow**
```bash
# Terminal 1: Scheduler
airflow scheduler

# Terminal 2: Webserver
airflow webserver --port 8080
```

### Running the Pipeline

**Manual execution:**
```bash
# Extract jobs
python -m src.extract.jobspy_extractor

# Run full pipeline
python -m dags.job_pipeline_dag
```

**Via Airflow:**
1. Open Airflow UI: http://localhost:8080
2. Enable the DAG: `job_pipeline_dag`
3. Trigger the DAG manually or wait for the scheduled run

## 📋 Database Schema

### Tables

**1. raw_job_postings** - Original scraped data
- `raw_job_id`: Primary key from scraper
- `source_platform`: LinkedIn, Indeed, Glassdoor, etc.
- `search_keyword`: Job title searched
- `title`, `company`, `location`: Job details
- `salary_min`, `salary_max`, `salary_currency`: Compensation
- `job_url`, `description`: Full job details
- `scraped_date`: When the job was scraped

**2. cleaned_job_postings** - Cleaned, standardized data
- `job_id`: Primary key
- `title_clean`, `company_clean`: Cleaned text
- `city`, `country`: Parsed location
- `remote_type`: Remote, Hybrid, On-site
- `seniority_level`: Junior, Mid, Senior
- `is_duplicate`: Duplicate detection flag
- `is_active`: Job still active flag

**3. job_skills** - Extracted skills from descriptions
- `job_id`, `skill_name`, `skill_category`
- Categories: Programming, BI Tools, Data Engineering, Cloud, German Language, Analytics

**4. job_match_scores** - Job relevance scoring
- `job_id`: Reference to job
- `match_score`: 0-100 relevance score
- `skill_match_count`: Number of matching skills
- `matched_skills`: Array of skills you have
- `missing_skills`: Array of skills you lack
- `german_requirement`: German language level required
- `experience_requirement`: Years of experience required
- `priority_level`: High, Medium, Low

**5. applications_tracker** - Manual application tracking
- `application_id`: Primary key
- `job_id`: Reference to job
- `application_status`: Not Applied, Applied, Rejected, Interview, Offer, Archived
- `applied_date`, `follow_up_date`: Important dates
- `cv_version_used`: Which CV version
- `notes`: Personal notes

## 🎯 Job Search Scope

**Job Titles:**
- Data Analyst
- BI Analyst
- Junior Data Engineer
- SQL Developer
- Power BI Analyst
- Data Engineer Intern / Junior
- Business Intelligence Developer

**Locations:**
- Berlin
- All German cities

**Platforms:**
- LinkedIn
- Indeed
- Glassdoor
- Google Jobs
- ZipRecruiter

## 👤 Your Profile

**Skills:**
- SQL, Python, Apache Airflow, PostgreSQL
- Power BI, Tableau
- ETL pipelines, Data validation, Dashboarding
- Oracle Database, Spark basics
- German B1/B2 (learning)

**Scoring Preferences:**
- ✅ Higher score: SQL, Python, Power BI, Airflow, PostgreSQL, ETL
- ✅ Higher score: Junior, Entry-level, Trainee, Analyst roles
- ✅ Higher score: Berlin, Remote Germany, Hybrid Berlin
- ❌ Lower score: C1/C2 German requirement
- ❌ Lower score: 5+ years experience requirement

## 📊 Dashboard KPIs

Access these via Power BI using the SQL views:

- **Total Jobs Scraped**: Running count of all jobs
- **New Jobs Today**: Jobs added in last 24 hours
- **High-Priority Jobs**: Count with priority_level = 'High'
- **Top Hiring Companies**: Companies with most open positions
- **Most Demanded Skills**: Skill frequency analysis
- **Jobs by City**: Geographic distribution
- **Jobs by Platform**: Source platform distribution
- **Average Match Score**: Mean relevance across jobs
- **Application Status Summary**: Status breakdown

## 🔧 Configuration

Create a `.env` file in the project root:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_market_db
DB_USER=your_username
DB_PASSWORD=your_password

# JobSpy
JOBSPY_TIMEOUT=30
JOBSPY_MAX_RESULTS=500

# Airflow
AIRFLOW_HOME=/path/to/airflow
AIRFLOW__CORE__DAGS_FOLDER=/path/to/dags

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pipeline.log
```

## ✅ Data Quality Checks

The pipeline validates:
- Job title is not null
- Company is not null
- Job URL is not null
- Duplicate detection (title + company + location + URL)
- scraped_date is always populated
- match_score is between 0-100
- No salary_min > salary_max
- Valid remote_type values

## 📝 Key Features

✅ **Automated Scraping** - Daily job posting collection
✅ **Data Cleaning** - Standardization and deduplication
✅ **Skill Extraction** - NLP-based skill detection
✅ **Relevance Scoring** - Personalized job matching
✅ **Duplicate Detection** - Prevent data redundancy
✅ **Quality Validation** - Ensure data integrity
✅ **Application Tracking** - Manual application management
✅ **Dashboard Ready** - Pre-built SQL views for Power BI
✅ **Error Handling** - Robust error management and logging
✅ **Modular Code** - Clean, reusable, well-documented

## 🚫 Important Notes

⚠️ **No Automated Applications** - This system only collects, analyzes, scores, and tracks jobs. All applications are manual.

⚠️ **Environment Variables** - Never hardcode passwords or API keys. Always use `.env`

⚠️ **PostgreSQL Required** - Some features require PostgreSQL-specific functions

## 📖 Documentation

Each module includes docstrings and comments. Key files:
- `src/utils/config.py` - Configuration management
- `src/extract/jobspy_extractor.py` - How to customize job searches
- `src/scoring/score_calculator.py` - Scoring logic details
- `sql/tables/` - Table schema explanations

## 🤝 Contributing

This is a personal portfolio project. Feel free to fork and customize for your own use!

## 📄 License

MIT License - See LICENSE file for details

## 🎓 Learning Outcomes

By building this project, you'll learn:
- End-to-end data pipeline design
- ETL best practices with Airflow
- PostgreSQL database design and queries
- Data quality and validation
- Python data engineering patterns
- Web scraping with JobSpy
- Dashboard design principles
- Git and GitHub best practices

## 📞 Support

For questions or issues:
1. Check the documentation in each module
2. Review the SQL schema in `sql/tables/`
3. Check Airflow logs for pipeline errors
4. Review test files for usage examples

---

**Last Updated:** June 2026
**Status:** In Development
