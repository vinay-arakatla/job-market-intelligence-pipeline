-- Applications Tracker Table
-- Stores manual application tracking

CREATE TABLE IF NOT EXISTS applications_tracker (
    application_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES cleaned_job_postings(job_id) ON DELETE CASCADE,
    application_status VARCHAR(50) NOT NULL CHECK (
        application_status IN ('Not Applied', 'Applied', 'Rejected', 'Interview', 'Offer', 'Archived')
    ),
    applied_date DATE,
    follow_up_date DATE,
    cv_version_used VARCHAR(100),
    cover_letter_used BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_application_job_id ON applications_tracker(job_id);
CREATE INDEX idx_application_status ON applications_tracker(application_status);
CREATE INDEX idx_application_applied_date ON applications_tracker(applied_date);
CREATE INDEX idx_application_follow_up_date ON applications_tracker(follow_up_date);

-- Unique constraint: one application entry per job
CREATE UNIQUE INDEX idx_job_application_unique ON applications_tracker(job_id);

-- Comment for documentation
COMMENT ON TABLE applications_tracker IS 
'Manual tracking of job applications and their status.
Statuses: Not Applied, Applied, Rejected, Interview, Offer, Archived';

COMMENT ON COLUMN applications_tracker.job_id IS 'Foreign key reference to cleaned_job_postings';
COMMENT ON COLUMN applications_tracker.application_status IS 'Current status of application';
COMMENT ON COLUMN applications_tracker.applied_date IS 'Date when application was submitted';
COMMENT ON COLUMN applications_tracker.follow_up_date IS 'Planned date for follow-up';
COMMENT ON COLUMN applications_tracker.cv_version_used IS 'Which version of CV was used (e.g., cv_v1, cv_data_engineer)';
COMMENT ON COLUMN applications_tracker.cover_letter_used IS 'Whether a cover letter was submitted';
COMMENT ON COLUMN applications_tracker.notes IS 'Personal notes about the application or interview';
