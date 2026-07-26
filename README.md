# Challenge Omid

Challenge Omid is a production-ready Telegram challenge management system with a clean Python backend, automatic daily exercise delivery, late submission tracking, and a professional FastAPI + SQLAdmin admin panel.

## Final Architecture

The application follows a strict layered architecture:

```text
Telegram/FastAPI Entry Points
        ↓
Handlers / Admin Views / Scheduler Jobs
        ↓
Services
        ↓
Repositories
        ↓
SQLAlchemy ORM
        ↓
SQLite in development / PostgreSQL-ready database
```

Business rules live in services. Bot handlers do not query, commit, or access the database directly.

## Project File Tree

```text
app/
  bot/
    handlers/
      registration.py
      submissions.py
    keyboards/
      contact.py
    middlewares/
      services.py
    states/
      registration.py
    routers.py
    runner.py
  admin/
    auth.py
    dashboard.py
    views.py
  core/
    config.py
    logger.py
  database/
    base.py
    session.py
    models/
      user.py
      challenge.py
      submission.py
    repositories/
      base.py
      user_repository.py
      challenge_repository.py
      submission_repository.py
  scheduler/
    jobs.py
    runner.py
  services/
    challenge_service.py
    exceptions.py
    metrics_service.py
    registration_service.py
    submission_service.py
    time.py
  main.py
alembic/
  env.py
  script.py.mako
  versions/
    0001_initial.py
logs/
tests/
.env
requirements.txt
README.md
```

## Installation Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
alembic upgrade head
```

## Required Environment Variables

The application reads settings from `.env` through `python-dotenv`.

```env
BOT_TOKEN=your-telegram-bot-token
DATABASE_URL=sqlite+aiosqlite:///./challenge_omid.db
MAX_USERS=400
TIMEZONE=Asia/Tehran
ADMIN_IDS=123456789,987654321
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password
SECRET_KEY=change-this-to-a-long-random-secret
AUTO_CREATE_DB=true
LOG_LEVEL=INFO
```

For PostgreSQL deployment, use an async SQLAlchemy URL:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/challenge_omid
```

Plain `postgresql://` URLs are automatically normalized to `postgresql+asyncpg://` by the central config layer.

## Running the Admin Panel

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

```text
http://localhost:8000/admin/dashboard
```

The dashboard shows:

- total users
- remaining capacity
- active challenge day
- today's submissions
- late users count

SQLAdmin includes searchable/filterable management pages for users, challenges, and submissions.

## Running the Telegram Bot

```bash
python -m app.bot.runner
```

The bot supports:

- `/start`
- registration onboarding
- name collection
- Telegram contact button phone collection
- capacity checking with the exact full-capacity message
- daily exercise delivery through APScheduler
- text answer collection
- automatic late submission detection
- `/status`

When the registration limit is reached, users receive:

```text
❌ ظرفیت چالش تکمیل شده است.
```

## Challenge Scheduling

Admins create challenge days from SQLAdmin. Each challenge has:

- day
- title
- description
- send time
- deadline
- active/inactive status

The scheduler checks every minute for active, unsent challenges whose send time has arrived and whose deadline has not passed. It sends the challenge to all active users and marks the challenge as sent.

## Database Models

### User

- id
- telegram_id
- name
- phone
- status
- created_at

### Challenge

- id
- day
- title
- description
- send_time
- deadline
- created_at
- is_active
- sent_at

### Submission

- id
- user_id
- challenge_id
- answer
- submitted_at
- is_late

Submissions are unique per user and challenge. If a participant resubmits for the same challenge, the answer is updated and the late flag is recalculated.

## Migrations

Create a migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Deployment Notes

- Keep `BOT_TOKEN`, `ADMIN_PASSWORD`, and `SECRET_KEY` in deployment secrets.
- Run the FastAPI admin panel and Telegram bot as separate processes.
- Use PostgreSQL in production.
- Keep one active bot polling process per Telegram bot token.
- Configure process supervision with systemd, Docker, Kubernetes, or another orchestrator.
- Logs are written to `logs/challenge_omid.log` and stdout.
