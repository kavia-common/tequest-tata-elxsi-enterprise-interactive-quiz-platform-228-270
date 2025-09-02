# TEQuestMonolithicContainer Deployment Guide

This document outlines deploying the Django monolith using Docker Compose (local_docker target).

Files added:
- Dockerfile: Builds Django app with Gunicorn, exposes port 3000
- docker-compose.yml: Orchestrates Postgres and the Django app
- entrypoint.sh: Waits for DB, runs migrations, collectstatic, ensures superuser, and starts Gunicorn
- .env.example: All required environment variables

Steps:
1) cd TEQuestMonolithicContainer
2) cp .env.example .env
3) Adjust environment variables:
   - ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD
   - DATABASE_URL (default uses db service)
   - EMAIL_* settings if SMTP is available
   - DJANGO_ALLOWED_HOSTS
4) docker compose up --build

Access:
- API: http://localhost:3000/api/
- Docs: http://localhost:3000/docs/
- Admin: http://localhost:3000/admin/

Static files:
- Collected to /app/staticfiles (mapped to static_volume)
- Serve via the Django app (sufficient for local usage). For production, place behind a reverse proxy (e.g., NGINX) to serve staticfiles directly.

Data persistence:
- PostgreSQL persistent data stored in volume db_data

Notes:
- SQLite is used if DATABASE_URL is not set. In docker-compose, DATABASE_URL defaults to Postgres.
- The container auto-creates a superuser if ADMIN_* variables are set.
