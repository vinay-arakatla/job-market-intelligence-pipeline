-- Dashboard View: Jobs Overview
-- Shows summary statistics and recent jobs

CREATE OR REPLACE VIEW vw_jobs_overview AS
SELECT
    COUNT(DISTINCT c.job_id) as total_jobs,
    COUNT(DISTINCT CASE WHEN c.is_active = TRUE THEN c.job_id END) as active_jobs,
    COUNT(DISTINCT CASE WHEN c.scraped_date::date = CURRENT_DATE THEN c.job_id END) as new_jobs_today,
    COUNT(DISTINCT c.company_clean) as unique_companies,
    COUNT(DISTINCT c.city) as unique_cities,
    ROUND(AVG(s.match_score)::numeric, 2) as avg_match_score,
    COUNT(DISTINCT CASE WHEN s.priority_level = 'High' THEN c.job_id END) as high_priority_count,
    COUNT(DISTINCT CASE WHEN s.priority_level = 'Medium' THEN c.job_id END) as medium_priority_count,
    COUNT(DISTINCT CASE WHEN s.priority_level = 'Low' THEN c.job_id END) as low_priority_count
FROM
    cleaned_job_postings c
    LEFT JOIN job_match_scores s ON c.job_id = s.job_id
WHERE
    c.is_active = TRUE;

-- Dashboard View: Top Hiring Companies
-- Shows companies with most open positions

CREATE OR REPLACE VIEW vw_top_hiring_companies AS
SELECT
    c.company_clean,
    COUNT(c.job_id) as open_positions,
    COUNT(DISTINCT c.city) as cities,
    ROUND(AVG(s.match_score)::numeric, 2) as avg_match_score,
    COUNT(DISTINCT CASE WHEN s.priority_level = 'High' THEN c.job_id END) as high_priority_jobs,
    STRING_AGG(DISTINCT c.city, ', ' ORDER BY c.city) as locations
FROM
    cleaned_job_postings c
    LEFT JOIN job_match_scores s ON c.job_id = s.job_id
WHERE
    c.is_active = TRUE
GROUP BY
    c.company_clean
ORDER BY
    open_positions DESC
LIMIT 20;

-- Dashboard View: Most Demanded Skills
-- Shows skills that appear most frequently in job descriptions

CREATE OR REPLACE VIEW vw_skills_demand AS
SELECT
    js.skill_category,
    js.skill_name,
    COUNT(DISTINCT js.job_id) as job_count,
    COUNT(DISTINCT c.company_clean) as company_count,
    ROUND(COUNT(DISTINCT js.job_id)::numeric / COUNT(DISTINCT c.job_id) * 100, 2) as percentage_of_jobs
FROM
    job_skills js
    INNER JOIN cleaned_job_postings c ON js.job_id = c.job_id
WHERE
    c.is_active = TRUE
GROUP BY
    js.skill_category,
    js.skill_name
ORDER BY
    job_count DESC;

-- Dashboard View: Jobs by Location
-- Shows distribution of jobs by city

CREATE OR REPLACE VIEW vw_jobs_by_location AS
SELECT
    c.city,
    c.country,
    COUNT(c.job_id) as total_jobs,
    COUNT(DISTINCT CASE WHEN c.remote_type = 'Remote' THEN c.job_id END) as remote_jobs,
    COUNT(DISTINCT CASE WHEN c.remote_type = 'Hybrid' THEN c.job_id END) as hybrid_jobs,
    COUNT(DISTINCT CASE WHEN c.remote_type = 'On-site' THEN c.job_id END) as onsite_jobs,
    ROUND(AVG(s.match_score)::numeric, 2) as avg_match_score,
    COUNT(DISTINCT CASE WHEN s.priority_level = 'High' THEN c.job_id END) as high_priority_count
FROM
    cleaned_job_postings c
    LEFT JOIN job_match_scores s ON c.job_id = s.job_id
WHERE
    c.is_active = TRUE
GROUP BY
    c.city,
    c.country
ORDER BY
    total_jobs DESC;

-- Dashboard View: High Priority Jobs
-- Shows jobs with score 80+

CREATE OR REPLACE VIEW vw_high_priority_jobs AS
SELECT
    c.job_id,
    c.title_clean,
    c.company_clean,
    c.city,
    c.remote_type,
    c.seniority_level,
    c.posted_date,
    s.match_score,
    s.skill_match_count,
    s.matched_skills,
    s.missing_skills,
    s.german_requirement,
    a.application_status,
    c.job_url
FROM
    cleaned_job_postings c
    INNER JOIN job_match_scores s ON c.job_id = s.job_id
    LEFT JOIN applications_tracker a ON c.job_id = a.job_id
WHERE
    c.is_active = TRUE
    AND s.priority_level = 'High'
ORDER BY
    s.match_score DESC,
    c.posted_date DESC;

-- Dashboard View: Application Status Summary
-- Shows breakdown of application statuses

CREATE OR REPLACE VIEW vw_application_status_summary AS
SELECT
    a.application_status,
    COUNT(a.application_id) as count,
    ROUND(COUNT(a.application_id)::numeric / (SELECT COUNT(*) FROM applications_tracker) * 100, 2) as percentage,
    MIN(a.applied_date) as first_applied,
    MAX(a.applied_date) as last_applied
FROM
    applications_tracker a
GROUP BY
    a.application_status
ORDER BY
    count DESC;

-- Dashboard View: Jobs by Posted Date
-- Shows job postings trend over time

CREATE OR REPLACE VIEW vw_jobs_by_posted_date AS
SELECT
    DATE(c.posted_date) as posted_date,
    COUNT(c.job_id) as job_count,
    COUNT(DISTINCT c.company_clean) as company_count,
    ROUND(AVG(s.match_score)::numeric, 2) as avg_match_score,
    COUNT(DISTINCT CASE WHEN s.priority_level = 'High' THEN c.job_id END) as high_priority_count
FROM
    cleaned_job_postings c
    LEFT JOIN job_match_scores s ON c.job_id = s.job_id
WHERE
    c.is_active = TRUE
    AND c.posted_date IS NOT NULL
GROUP BY
    DATE(c.posted_date)
ORDER BY
    posted_date DESC;

-- Dashboard View: Match Score Distribution
-- Shows distribution of jobs by match score ranges

CREATE OR REPLACE VIEW vw_match_score_distribution AS
SELECT
    CASE
        WHEN s.match_score >= 80 THEN 'High (80-100)'
        WHEN s.match_score >= 50 THEN 'Medium (50-79)'
        ELSE 'Low (0-49)'
    END as score_range,
    COUNT(c.job_id) as job_count,
    ROUND(COUNT(c.job_id)::numeric / (SELECT COUNT(*) FROM cleaned_job_postings WHERE is_active = TRUE) * 100, 2) as percentage,
    ROUND(AVG(s.match_score)::numeric, 2) as avg_score,
    MIN(s.match_score) as min_score,
    MAX(s.match_score) as max_score
FROM
    cleaned_job_postings c
    INNER JOIN job_match_scores s ON c.job_id = s.job_id
WHERE
    c.is_active = TRUE
GROUP BY
    score_range
ORDER BY
    avg_score DESC;
