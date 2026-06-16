-- Job Match Scores Table
-- Stores relevance score for each job based on user profile

CREATE TABLE IF NOT EXISTS job_match_scores (
    match_score_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL UNIQUE REFERENCES cleaned_job_postings(job_id) ON DELETE CASCADE,
    match_score DECIMAL(5, 2) NOT NULL CHECK (match_score >= 0 AND match_score <= 100),
    skill_match_count INTEGER DEFAULT 0,
    matched_skills TEXT[],
    missing_skills TEXT[],
    german_requirement VARCHAR(50),
    experience_requirement_min INTEGER,
    experience_requirement_max INTEGER,
    priority_level VARCHAR(20) CHECK (priority_level IN ('High', 'Medium', 'Low')),
    calculated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_match_score_value ON job_match_scores(match_score);
CREATE INDEX idx_priority_level ON job_match_scores(priority_level);
CREATE INDEX idx_match_calculated_at ON job_match_scores(calculated_at);
CREATE INDEX idx_match_skill_count ON job_match_scores(skill_match_count);

-- Comment for documentation
COMMENT ON TABLE job_match_scores IS 
'Job relevance scores calculated based on user profile.
Score is 0-100: 80+ (High), 50-79 (Medium), <50 (Low priority)';

COMMENT ON COLUMN job_match_scores.job_id IS 'Foreign key reference to cleaned_job_postings';
COMMENT ON COLUMN job_match_scores.match_score IS 'Relevance score 0-100 for this job';
COMMENT ON COLUMN job_match_scores.skill_match_count IS 'Number of user skills that match job requirements';
COMMENT ON COLUMN job_match_scores.matched_skills IS 'Array of skills user has that match job';
COMMENT ON COLUMN job_match_scores.missing_skills IS 'Array of skills job requires but user lacks';
COMMENT ON COLUMN job_match_scores.german_requirement IS 'German language level required: None, A1, A2, B1, B2, C1, C2';
COMMENT ON COLUMN job_match_scores.experience_requirement_min IS 'Minimum years of experience required';
COMMENT ON COLUMN job_match_scores.experience_requirement_max IS 'Maximum years of experience (usually for mid-level)';
COMMENT ON COLUMN job_match_scores.priority_level IS 'Priority category: High (80+), Medium (50-79), Low (<50)';
