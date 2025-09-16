#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database initialization script for Elevate.AI (PostgreSQL version for Render)

This script initializes the PostgreSQL database with the necessary tables
for the Elevate.AI application.

Usage on Render (as a Job):
    python init_db.py
"""

import os
import psycopg2  # CHANGED: Use psycopg2 for PostgreSQL instead of sqlite3
from datetime import datetime
from utils.config import get_config
from utils.logger import get_logger, log_info, log_error

# Initialize logger
logger = get_logger()

# Get configuration
config = get_config()

# CHANGED: Database connection is now handled by an environment variable from Render
DATABASE_URL = os.environ.get('DATABASE_URL')

# SQL statements to create tables for PostgreSQL
CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS resumes (
        id SERIAL PRIMARY KEY,  -- CHANGED: SERIAL PRIMARY KEY for auto-incrementing in PostgreSQL
        user_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        content TEXT NOT NULL,
        job_description TEXT NOT NULL,
        analysis TEXT,
        match_score REAL,
        strengths TEXT,
        gaps TEXT,
        suggestions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS interviews (
        id SERIAL PRIMARY KEY,  -- CHANGED
        user_id TEXT NOT NULL,
        job_role TEXT NOT NULL,
        questions TEXT NOT NULL,
        answers TEXT,
        feedback TEXT,
        overall_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS syllabi (
        id SERIAL PRIMARY KEY,  -- CHANGED
        user_id TEXT NOT NULL,
        subject TEXT NOT NULL,
        content TEXT NOT NULL,
        parsed_topics TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS quizzes (
        id SERIAL PRIMARY KEY,  -- CHANGED
        user_id TEXT NOT NULL,
        syllabus_id INTEGER NOT NULL,
        topics TEXT NOT NULL,
        questions TEXT NOT NULL,
        answers TEXT,
        score REAL,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (syllabus_id) REFERENCES syllabi (id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS study_plans (
        id SERIAL PRIMARY KEY,  -- CHANGED
        user_id TEXT NOT NULL,
        syllabus_id INTEGER NOT NULL,
        duration_days INTEGER NOT NULL,
        hours_per_day REAL NOT NULL,
        plan_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (syllabus_id) REFERENCES syllabi (id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS progress (
        id SERIAL PRIMARY KEY,  -- CHANGED
        user_id TEXT NOT NULL,
        syllabus_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        mastery_level REAL NOT NULL,
        quiz_count INTEGER DEFAULT 0,
        study_hours REAL DEFAULT 0,
        last_quiz_id INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (syllabus_id) REFERENCES syllabi (id),
        FOREIGN KEY (last_quiz_id) REFERENCES quizzes (id)
    )
    """
]

# A new helper function to get the connection
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set!")
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Initialize the database with required tables"""
    log_info("Initializing PostgreSQL database...")
    
    # CHANGED: Removed file system logic (os.makedirs) as it's not needed.
    
    conn = None  # Initialize conn to None
    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Create tables
            for create_table_sql in CREATE_TABLES:
                cursor.execute(create_table_sql)
        
        # Commit changes
        conn.commit()
        log_info("Database initialization complete! Tables created.")
    except Exception as e:
        log_error(f"Error initializing database: {str(e)}")
        if conn:
            conn.rollback() # Rollback changes on error
        raise
    finally:
        if conn:
            conn.close() # Always close the connection

# NOTE: The `add_sample_data` function is kept here for your reference,
# but it is NOT recommended to run it on a production database.
# It would also need to be updated to use `%s` placeholders and `RETURNING id`.
# We will not call it from the main execution block.

if __name__ == "__main__":
    try:
        log_info(f"Starting database initialization for {config.APP_NAME}")
        init_db()
        
        # CHANGED: Removed the interactive input() part.
        # The job will now run to completion without needing user input.
        
        log_info("Database setup job finished successfully!")
        print("Database setup job finished successfully!")
    except Exception as e:
        log_error(f"Database setup failed: {str(e)}")
        print(f"Database setup failed: {str(e)}")
        exit(1)