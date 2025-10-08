-- Gmail Agent Database Schema
-- PostgreSQL Version
-- Note: Database 'gmail_agent_db' is already created by POSTGRES_DB env var

-- ============================================================
-- Table 1: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    refresh_token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Table 2: emails
-- ============================================================
CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    gmail_message_id VARCHAR(100) NOT NULL UNIQUE,
    subject TEXT,
    sender_email VARCHAR(255) NOT NULL,
    sender_name VARCHAR(255),
    body_text TEXT,
    email_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- Table 3: gmail_agent_dataset
-- ============================================================
DO $$ BEGIN
    CREATE TYPE lead_result AS ENUM ('generate_lead', 'no_lead');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS gmail_agent_dataset (
    id SERIAL PRIMARY KEY,
    email_id INT NOT NULL UNIQUE,
    user_id INT NOT NULL,
    model_result lead_result NOT NULL,
    user_feedback lead_result NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Trigger to auto-update updated_at
CREATE TRIGGER update_gmail_agent_dataset_updated_at BEFORE UPDATE ON gmail_agent_dataset
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
