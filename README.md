# tequest-tata-elxsi-enterprise-interactive-quiz-platform-228-270

TEQuest Monolithic (Django backend, React front planned). This repository currently includes the Django REST API foundations:

- User registration/login/logout, profile management
- Role-based access (participant/admin via UserProfile)
- Quiz types: MCQ and Crossword (models and basic flow)
- Attempts, submissions, scoring, and leaderboard
- Admin endpoints: stats and audit logs
- Email notifications (welcome, attempt submitted, password reset)
- OpenAPI/Swagger docs at /docs/

## Quickstart (local, non-Docker)
- Install Python deps (see TEQuestMonolithicContainer/requirements.txt)
- Copy .env.example to .env and adjust values (inside TEQuestMonolithicContainer/)
- Run migrations: python manage.py makemigrations && python manage.py migrate
- Create superuser (two options):
  1) Interactive: python manage.py createsuperuser
  2) Automatic from env vars (recommended for deploys): see "Automatic superuser creation" below
- Start server (bind to port 3000 for deployment readiness):
  python manage.py runserver 0.0.0.0:3000

### Automatic superuser creation
- If the following environment variables are set in TEQuestMonolithicContainer/.env, a Django superuser will be created automatically at startup (during runserver/migrate/collectstatic) if not already present:
  - ADMIN_USERNAME
  - ADMIN_EMAIL
  - ADMIN_PASSWORD
- You can also trigger this explicitly at any time:
  python manage.py ensure_superuser
- This process is idempotent and will not recreate an existing user with the same username.

Admin login:
- Once created, you can log in to /admin using the configured credentials.

## Dockerized deployment (local_docker)

The TEQuestMonolithicContainer includes:
- Dockerfile optimized for Django + Gunicorn
- docker-compose.yml orchestrating:
  - Postgres 15 (db service)
  - Django app (web service)
- entrypoint.sh which:
  - waits for DB readiness when using Postgres
  - runs migrations
  - collects static files into /app/staticfiles
  - ensures superuser creation using ADMIN_* env vars
  - launches Gunicorn on port 3000

### Steps
1) cd TEQuestMonolithicContainer
2) cp .env.example .env
3) Update .env values as needed (especially ADMIN_* and email settings)
4) docker compose up --build

The API will be available at:
- http://localhost:3000/api/
Docs:
- http://localhost:3000/docs/

To stop:
- docker compose down

Persisted data:
- Postgres data volume: db_data
- Static files volume: static_volume

### Environment variables
- .env is loaded by docker-compose and passed to the web container.
- DATABASE_URL controls using Postgres (default provided in .env.example).
- DJANGO_ALLOWED_HOSTS must include the host used to access the container (localhost by default).
- SITE_URL and PASSWORD_RESET_PATH are used in password reset emails.

### Local development (SQLite)
If you prefer to run without Docker for local dev, or with SQLite:
- Do not set DATABASE_URL in your environment. Django will fallback to SQLite.

## API highlights
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET|PATCH /api/auth/me
- POST /api/auth/password-reset
- POST /api/auth/password-reset/confirm
- GET /api/quizzes
- GET /api/quizzes/{id}
- POST /api/quizzes/{id}/attempts/start
- POST /api/attempts/{attempt_id}/mcq/submit
- POST /api/attempts/{attempt_id}/crossword/submit
- POST /api/attempts/{attempt_id}/finalize
- GET /api/quizzes/{id}/leaderboard
- GET /api/admin/stats
- GET /api/admin/audit-logs

## Environment
- Copy TEQuestMonolithicContainer/.env.example and set values.
- Email and SITE_URL should be configured for password reset flows.

## Notes
- The deployment listens on port 3000 internally and externally via docker-compose mapping.
- Ensure you set DJANGO_SECRET_KEY and DJANGO_DEBUG=false for production-like environments.

Next steps:
- Add React frontend scaffolding and integrate with these APIs.
- SSO integration hooks.
- Expand analytics and admin tooling.