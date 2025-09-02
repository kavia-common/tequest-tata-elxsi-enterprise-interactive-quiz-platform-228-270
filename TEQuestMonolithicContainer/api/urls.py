from django.urls import path
from . import views

urlpatterns = [
    # Health
    path('health/', views.health, name='Health'),

    # Auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/me/', views.me, name='me'),
    path('auth/password-reset/', views.request_password_reset, name='password-reset'),
    path('auth/password-reset/confirm/', views.confirm_password_reset, name='password-reset-confirm'),

    # Quizzes and attempts
    path('quizzes/', views.list_quizzes, name='quizzes'),
    path('quizzes/my/', views.my_quizzes, name='my-quizzes'),
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz-detail'),
    path('quizzes/<int:quiz_id>/attempts/start/', views.start_attempt, name='attempt-start'),

    # Submissions
    path('attempts/<int:attempt_id>/mcq/submit/', views.submit_mcq_answer, name='mcq-submit'),
    path('attempts/<int:attempt_id>/crossword/submit/', views.submit_crossword_answer, name='crossword-submit'),
    path('attempts/<int:attempt_id>/finalize/', views.finalize_attempt, name='attempt-finalize'),

    # Leaderboard
    path('quizzes/<int:quiz_id>/leaderboard/', views.leaderboard, name='leaderboard'),

    # Admin
    path('admin/stats/', views.admin_stats, name='admin-stats'),
    path('admin/audit-logs/', views.audit_logs, name='audit-logs'),
]
