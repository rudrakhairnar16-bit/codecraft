from __future__ import annotations

import duckdb

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS files (
    path VARCHAR PRIMARY KEY,
    hash VARCHAR,
    size INTEGER,
    lines INTEGER,
    first_scanned TIMESTAMP,
    last_modified TIMESTAMP,
    last_scanned TIMESTAMP,
    complexity DOUBLE,
    import_count INTEGER
);

CREATE TABLE IF NOT EXISTS concepts (
    name VARCHAR PRIMARY KEY,
    tier INTEGER,
    category VARCHAR,
    description VARCHAR
);

CREATE TABLE IF NOT EXISTS file_concepts (
    file_path VARCHAR,
    concept_name VARCHAR,
    occurrences INTEGER DEFAULT 1,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    PRIMARY KEY (file_path, concept_name)
);

CREATE SEQUENCE IF NOT EXISTS seq_debt_items START 1;

CREATE TABLE IF NOT EXISTS debt_items (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_debt_items'),
    file_path VARCHAR,
    pattern_type VARCHAR,
    pattern_location VARCHAR,
    old_snippet VARCHAR,
    suggestion VARCHAR,
    alternative_code VARCHAR,
    difficulty INTEGER,
    tier_gap INTEGER,
    resolved BOOLEAN DEFAULT FALSE,
    created TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE SEQUENCE IF NOT EXISTS seq_challenge_history START 1;

CREATE TABLE IF NOT EXISTS challenge_history (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_challenge_history'),
    challenge_type VARCHAR,
    concept_name VARCHAR,
    correct BOOLEAN,
    hints_used INTEGER DEFAULT 0,
    time_taken_seconds INTEGER DEFAULT 0,
    domain VARCHAR DEFAULT 'general',
    created TIMESTAMP
);

CREATE TABLE IF NOT EXISTS spaced_repetition (
    concept_name VARCHAR PRIMARY KEY,
    ease_factor DOUBLE DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review TIMESTAMP,
    last_review TIMESTAMP,
    strength DOUBLE DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR PRIMARY KEY,
    value VARCHAR
);

CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_challenge_history'),
    scan_type VARCHAR,
    file_count INTEGER,
    concept_count INTEGER,
    debt_count INTEGER,
    duration_seconds DOUBLE,
    created TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suggestions (
    concept_name VARCHAR PRIMARY KEY,
    reason VARCHAR,
    priority INTEGER DEFAULT 0,
    created TIMESTAMP
);
"""


def run_migrations(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(SCHEMA_SQL)

    row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
    current_version = row[0] if row[0] else 0

    if current_version < 1:
        conn.execute("INSERT INTO schema_version (version) VALUES (1)")

    if current_version < 2:
        from codecraft.models.concept import ConceptTaxonomy
        for c in ConceptTaxonomy.all():
            conn.execute(
                "INSERT OR IGNORE INTO concepts (name, tier, category, description) VALUES (?, ?, ?, ?)",
                [c.name, c.tier.value, c.category, c.description],
            )
        conn.execute("INSERT INTO schema_version (version) VALUES (2)")

    if current_version < 3:
        from codecraft.models.concept import ConceptTaxonomy
        for c in ConceptTaxonomy.all():
            conn.execute(
                "INSERT OR IGNORE INTO concepts (name, tier, category, description) VALUES (?, ?, ?, ?)",
                [c.name, c.tier.value, c.category, c.description],
            )
        conn.execute("INSERT INTO schema_version (version) VALUES (3)")
