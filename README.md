# tequest-tata-elxsi-enterprise-interactive-quiz-platform-228-270

TEQuest Monolithic (Django backend, React front planned). This repository currently includes the Django REST API foundations:

- User registration/login/logout, profile management
- Role-based access (participant/admin via UserProfile)
- Quiz types: MCQ and Crossword (models and basic flow)
- Attempts, submissions, scoring, and leaderboard
- Admin endpoints: stats and audit logs
- Email notifications (welcome, attempt submitted, password reset)
- OpenAPI/Swagger docs at /docs/

Quickstart:
- Install Python deps (see TEQuestMonolithicContainer/requirements.txt)
- Copy .env.example to .env and adjust values (inside TEQuestMonolithicContainer/)
- Run migrations: python manage.py makemigrations && python manage.py migrate
- Create superuser: python manage.py createsuperuser
- Start server (bind to port 3000 for deployment readiness):
  python manage.py runserver 0.0.0.0:3000

API highlights:
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

Environment:
- Copy TEQuestMonolithicContainer/.env.example and set values.
- Email and SITE_URL should be configured for password reset flows.

Next steps:
- Add React frontend scaffolding and integrate with these APIs.
- Switch DB to PostgreSQL and configure via env in settings.
- Add SSO integration hooks.
- Expand analytics and admin tooling.