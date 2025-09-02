from django.contrib import admin
from .models import (
    UserProfile, Quiz, MCQQuestion, Crossword, CrosswordClue,
    Attempt, LeaderboardEntry, AuditLog
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'display_name', 'organization')
    search_fields = ('user__username', 'display_name', 'organization')
    list_filter = ('role',)

class MCQInline(admin.TabularInline):
    model = MCQQuestion
    extra = 0

class CrosswordClueInline(admin.TabularInline):
    model = CrosswordClue
    extra = 0

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'is_published', 'start_time', 'end_time', 'total_points')
    list_filter = ('type', 'is_published')
    search_fields = ('title', 'description')
    inlines = [MCQInline]

@admin.register(Crossword)
class CrosswordAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'rows', 'cols')
    inlines = [CrosswordClueInline]

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'started_at', 'ended_at', 'score', 'is_submitted')
    list_filter = ('is_submitted', 'quiz__type')

@admin.register(LeaderboardEntry)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user', 'best_score', 'attempts_count', 'last_attempt_at')
    list_filter = ('quiz',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'created_at')
    search_fields = ('action',)
