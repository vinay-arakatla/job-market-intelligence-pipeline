-- Job Skills Table
-- Stores extracted skills from job descriptions
-- Linked to cleaned_job_postings

CREATE TABLE IF NOT EXISTS job_skills (
    job_skill_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES cleaned_job_postings(job_id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    skill_category VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(3, 2) DEFAULT 1.0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_job_skills_job_id ON job_skills(job_id);
CREATE INDEX idx_job_skills_skill_name ON job_skills(skill_name);
CREATE INDEX idx_job_skills_skill_category ON job_skills(skill_category);
CREATE INDEX idx_job_skills_job_category ON job_skills(job_id, skill_category);

-- Unique constraint to prevent duplicate skill entries per job
CREATE UNIQUE INDEX idx_job_skill_unique ON job_skills(job_id, skill_name);

-- Comment for documentation
COMMENT ON TABLE job_skills IS 
'Extracted skills from job descriptions. Each row represents a skill required for a job.
Skill categories: Programming, BI Tools, Data Engineering, Cloud, German Language, Analytics';

COMMENT ON COLUMN job_skills.job_id IS 'Foreign key reference to cleaned_job_postings';
COMMENT ON COLUMN job_skills.skill_name IS 'Name of the skill (e.g., Python, SQL, Power BI)';
COMMENT ON COLUMN job_skills.skill_category IS 'Category of skill for grouping and analysis';
COMMENT ON COLUMN job_skills.confidence_score IS 'Extraction confidence (0-1), higher means more confident';
