-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);


-- Create goals table
CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add a column to store the weekly plan JSON in the goals table
ALTER TABLE goals ADD COLUMN weekly_plan_json TEXT;


-- Create weekly_plans table
CREATE TABLE weekly_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);


-- Create tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    goal_id INTEGER,
    day TEXT,
    description TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    is_custom INTEGER DEFAULT 0,
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);


-- Insert a predefined test user
INSERT INTO users (name, email, password_hash) VALUES ('Test User', 'test@example.com', 'testhash');
