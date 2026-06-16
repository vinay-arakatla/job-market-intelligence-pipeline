-- Cleaned Job Postings Table
-- Stores cleaned and standardized job data
-- This table is used for analysis and scoring

CREATE TABLE IF NOT EXISTS cleaned_job_postings (
    job_id SERIAL PRIMARY KEY,
    raw_job_id INTEGER REFERENCES raw_job_postings(raw_job_id),
    source_platform VARCHAR(50) NOT NULL,
    title_clean VARCHAR(500) NOT NULL,
    company_clean VARCHAR(500) NOT NULL,
    city VARCHAR(255),
    country VARCHAR(100) DEFAULT 'Germany',
    remote_type VARCHAR(50),
    employment_type VARCHAR(100),
    seniority_level VARCHAR(100),
    salary_min DECIMAL(12, 2),
    salary_max DECIMAL(12, 2),
    salary_currency VARCHAR(10),
    posted_date TIMESTAMP,
    scraped_date TIMESTAMP NOT NULL,
    job_url TEXT UNIQUE NOT NULL,
    description_clean TEXT,
    is_duplicate BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_cleaned_source_platform ON cleaned_job_postings(source_platform);
CREATE INDEX idx_cleaned_city ON cleaned_job_postings(city);
CREATE INDEX idx_cleaned_seniority ON cleaned_job_postings(seniority_level);
CREATE INDEX idx_cleaned_remote_type ON cleaned_job_postings(remote_type);
CREATE INDEX idx_cleaned_is_active ON cleaned_job_postings(is_active);
CREATE INDEX idx_cleaned_is_duplicate ON cleaned_job_postings(is_duplicate);
CREATE INDEX idx_cleaned_scraped_date ON cleaned_job_postings(scraped_date);
CREATE INDEX idx_cleaned_posted_date ON cleaned_job_postings(posted_date);

-- Comment for documentation
COMMENT ON TABLE cleaned_job_postings IS 
'Cleaned and standardized job data. Derived from raw_job_postings table after data cleaning and transformation.
Used for analysis, scoring, and Power BI dashboards.';

COMMENT ON COLUMN cleaned_job_postings.job_id IS 'Primary key - unique job identifier';
COMMENT ON COLUMN cleaned_job_postings.raw_job_id IS 'Foreign key reference to raw_job_postings';
COMMENT ON COLUMN cleaned_job_postings.title_clean IS 'Standardized job title (cleaned and normalized)';
COMMENT ON COLUMN cleaned_job_postings.company_clean IS 'Standardized company name';
COMMENT ON COLUMN cleaned_job_postings.city IS 'Parsed city from location';
COMMENT ON COLUMN cleaned_job_postings.country IS 'Country (primarily Germany)';
COMMENT ON COLUMN cleaned_job_postings.remote_type IS 'Remote, Hybrid, or On-site';
COMMENT ON COLUMN cleaned_job_postings.employment_type IS 'Full-time, Part-time, Contract, Intern, etc.';
COMMENT ON COLUMN cleaned_job_postings.seniority_level IS 'Entry-level, Mid-level, Senior, Lead, etc.';
COMMENT ON COLUMN cleaned_job_postings.is_duplicate IS 'TRUE if marked as duplicate based on title+company+location+url';
COMMENT ON COLUMN cleaned_job_postings.is_active IS 'TRUE if job is still active, FALSE if expired or removed';
