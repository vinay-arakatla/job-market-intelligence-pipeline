-- Raw Job Postings Table
-- Stores original scraped data without heavy transformation
-- This is the landing zone for all scraped job data

CREATE TABLE IF NOT EXISTS raw_job_postings (
    raw_job_id SERIAL PRIMARY KEY,
    source_platform VARCHAR(50) NOT NULL,
    search_keyword VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(500) NOT NULL,
    location VARCHAR(500),
    job_type VARCHAR(100),
    job_level VARCHAR(100),
    salary_min DECIMAL(12, 2),
    salary_max DECIMAL(12, 2),
    salary_currency VARCHAR(10),
    salary_interval VARCHAR(50),
    posted_date TIMESTAMP,
    scraped_date TIMESTAMP NOT NULL DEFAULT NOW(),
    job_url TEXT UNIQUE NOT NULL,
    company_url TEXT,
    description TEXT,
    raw_data_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_raw_source_platform ON raw_job_postings(source_platform);
CREATE INDEX idx_raw_search_keyword ON raw_job_postings(search_keyword);
CREATE INDEX idx_raw_company ON raw_job_postings(company);
CREATE INDEX idx_raw_scraped_date ON raw_job_postings(scraped_date);
CREATE INDEX idx_raw_posted_date ON raw_job_postings(posted_date);
CREATE INDEX idx_raw_job_url ON raw_job_postings(job_url);

-- Comment for documentation
COMMENT ON TABLE raw_job_postings IS 
'Landing zone for raw scraped job data. Contains original data as received from JobSpy without transformation.
Used as the source for the cleaned_job_postings table in the transform stage.';

COMMENT ON COLUMN raw_job_postings.raw_job_id IS 'Primary key - auto-incremented ID';
COMMENT ON COLUMN raw_job_postings.source_platform IS 'Job platform source: linkedin, indeed, glassdoor, google, etc.';
COMMENT ON COLUMN raw_job_postings.search_keyword IS 'Job title searched (e.g., Data Analyst, BI Analyst)';
COMMENT ON COLUMN raw_job_postings.title IS 'Original job title as posted';
COMMENT ON COLUMN raw_job_postings.company IS 'Company name as posted';
COMMENT ON COLUMN raw_job_postings.location IS 'Location as posted (may need parsing)';
COMMENT ON COLUMN raw_job_postings.job_type IS 'Type of employment: Full-time, Part-time, Contract, etc.';
COMMENT ON COLUMN raw_job_postings.job_level IS 'Experience level: Entry-level, Mid-level, Senior, etc.';
COMMENT ON COLUMN raw_job_postings.salary_min IS 'Minimum salary if available';
COMMENT ON COLUMN raw_job_postings.salary_max IS 'Maximum salary if available';
COMMENT ON COLUMN raw_job_postings.salary_currency IS 'Currency code (EUR, USD, etc.)';
COMMENT ON COLUMN raw_job_postings.salary_interval IS 'Salary interval: yearly, monthly, hourly, etc.';
COMMENT ON COLUMN raw_job_postings.posted_date IS 'When the job was originally posted';
COMMENT ON COLUMN raw_job_postings.scraped_date IS 'When we scraped the job (server time)';
COMMENT ON COLUMN raw_job_postings.job_url IS 'Direct URL to the job posting';
COMMENT ON COLUMN raw_job_postings.company_url IS 'Company website URL if available';
COMMENT ON COLUMN raw_job_postings.description IS 'Full job description text';
COMMENT ON COLUMN raw_job_postings.raw_data_json IS 'Raw JSON data from JobSpy for reference';
