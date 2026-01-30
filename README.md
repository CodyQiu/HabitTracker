# Habit Tracker (Flask)

Simple habit tracking app built with Flask, Flask-Login, and SQLite. Users can register/login, add habits, run a timer, and view analytics of completed habit durations.

Live site (may take a minute to load, due to use of free version of Render):

```
https://habittracker-nbit.onrender.com
```

## Features

- User registration and login
- Add and list habits
- Start a habit timer and mark completion
- Analytics view for total time spent per habit

## Tech Stack

- Python + Flask
- Flask-Login (auth)
- Flask-Session (server-side sessions)
- SQLite (`myapp.db`)

## Local Setup

1. Create and activate a virtual environment

```
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Ensure the SQLite schema exists

```
sqlite3 myapp.db <<'SQL'
CREATE TABLE users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  hash TEXT NOT NULL
);
CREATE TABLE habits(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  habit TEXT NOT NULL,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  duration INTEGER,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE completions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  habit_id INTEGER,
  duration INTEGER,
  completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
SQL
```

4. Run the app (dev)

```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## Environment Variables

- `SECRET_KEY` (required in production)
- `SESSION_COOKIE_SECURE` (set to `true` in production)
- `SESSION_COOKIE_SAMESITE` (defaults to `Lax`)

## Production (Render)

Build command:

```
pip install -r requirements.txt
```

Start command:

```
gunicorn app:app --bind 0.0.0.0:$PORT
```

Notes:

- SQLite is file-based; for multiple workers or scaling, consider Postgres.
- `SESSION_TYPE=filesystem` stores sessions on disk; add a persistent disk or switch to another backend for production.
