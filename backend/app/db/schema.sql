PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS roles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    role_id         INTEGER NOT NULL REFERENCES roles(id),
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);

CREATE TABLE IF NOT EXISTS challenges (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    difficulty      TEXT NOT NULL CHECK (difficulty IN ('Beginner','Intermediate','Advanced','Expert')),
    category        TEXT NOT NULL,
    languages       TEXT NOT NULL,
    input_spec      TEXT,
    output_spec     TEXT,
    constraints     TEXT,
    examples        TEXT,
    time_limit_ms   INTEGER NOT NULL DEFAULT 2000,
    memory_limit_mb INTEGER NOT NULL DEFAULT 256,
    status          TEXT NOT NULL DEFAULT 'Draft'
                    CHECK (status IN ('Draft','Published','Archived')),
    created_by      INTEGER NOT NULL REFERENCES users(id),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_challenges_status ON challenges(status);

CREATE TABLE IF NOT EXISTS test_cases (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id    INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    input           TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_hidden       INTEGER NOT NULL DEFAULT 0,
    weight          INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_test_cases_challenge ON test_cases(challenge_id);

CREATE TABLE IF NOT EXISTS assessments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    manager_id      INTEGER NOT NULL REFERENCES users(id),
    starts_at       TEXT NOT NULL,
    ends_at         TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'Draft'
                    CHECK (status IN ('Draft','Active','Closed')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS assessment_challenges (
    assessment_id   INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    challenge_id    INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    PRIMARY KEY (assessment_id, challenge_id)
);

CREATE TABLE IF NOT EXISTS assessment_candidates (
    assessment_id   INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    candidate_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at      TEXT,
    submitted_at    TEXT,
    status          TEXT NOT NULL DEFAULT 'Assigned'
                    CHECK (status IN ('Assigned','InProgress','Submitted','Expired')),
    PRIMARY KEY (assessment_id, candidate_id)
);

CREATE TABLE IF NOT EXISTS submissions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    challenge_id    INTEGER NOT NULL REFERENCES challenges(id),
    assessment_id   INTEGER REFERENCES assessments(id),
    language        TEXT NOT NULL CHECK (language IN ('python','javascript','cpp')),
    source_code     TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'Queued'
                    CHECK (status IN ('Queued','Running','Accepted','WrongAnswer',
                                      'TimeLimitExceeded','MemoryLimitExceeded',
                                      'CompilationError','RuntimeError','InternalError','Cancelled')),
    submitted_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_challenge ON submissions(challenge_id);

CREATE TABLE IF NOT EXISTS execution_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id   INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    test_case_id    INTEGER NOT NULL REFERENCES test_cases(id),
    passed          INTEGER NOT NULL,
    actual_output   TEXT,
    duration_ms     REAL NOT NULL DEFAULT 0,
    memory_kb       REAL NOT NULL DEFAULT 0,
    exit_code       INTEGER,
    stderr          TEXT
);
CREATE INDEX IF NOT EXISTS idx_exec_results_submission ON execution_results(submission_id);

CREATE TABLE IF NOT EXISTS execution_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id   INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    level           TEXT NOT NULL,
    message         TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_exec_logs_submission ON execution_logs(submission_id);

CREATE TABLE IF NOT EXISTS leaderboard (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id    INTEGER NOT NULL REFERENCES users(id),
    challenge_id    INTEGER NOT NULL REFERENCES challenges(id),
    score           REAL NOT NULL DEFAULT 0,
    awarded_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (candidate_id, challenge_id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id         INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme           TEXT NOT NULL DEFAULT 'dark',
    editor_font     INTEGER NOT NULL DEFAULT 14,
    prefs_json      TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS system_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT NOT NULL,
    payload         TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type);