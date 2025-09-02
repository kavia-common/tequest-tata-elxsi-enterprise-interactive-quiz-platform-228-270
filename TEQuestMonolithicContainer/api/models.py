from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Choices and constants
ROLE_CHOICES = (
    ('participant', 'Participant'),
    ('admin', 'Admin'),
)

QUIZ_TYPE_CHOICES = (
    ('mcq', 'Multiple Choice'),
    ('crossword', 'Crossword'),
)

# PUBLIC_INTERFACE
class UserProfile(models.Model):
    """Extended profile for role-based access and user metadata."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='participant')
    display_name = models.CharField(max_length=120, blank=True)
    organization = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# PUBLIC_INTERFACE
class Quiz(models.Model):
    """Quiz model that supports both MCQ and Crossword with time windows and scoring rules."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=16, choices=QUIZ_TYPE_CHOICES, default='mcq')
    is_published = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_limit_seconds = models.PositiveIntegerField(default=0, help_text="0 means no limit.")
    max_attempts = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='quizzes_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_points = models.PositiveIntegerField(default=0)

    def is_active(self) -> bool:
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True

    def __str__(self):
        return f"{self.title} [{self.type}]"

# PUBLIC_INTERFACE
class MCQQuestion(models.Model):
    """MCQ question bank per quiz."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='mcq_questions')
    text = models.TextField()
    option_a = models.CharField(max_length=512)
    option_b = models.CharField(max_length=512)
    option_c = models.CharField(max_length=512, blank=True)
    option_d = models.CharField(max_length=512, blank=True)
    correct_option = models.CharField(max_length=1, choices=(('A','A'),('B','B'),('C','C'),('D','D')))
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q{self.order} - {self.quiz.title}"

# PUBLIC_INTERFACE
class Crossword(models.Model):
    """Crossword metadata associated to a quiz with 'crossword' type."""
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, related_name='crossword')
    rows = models.PositiveIntegerField(default=10)
    cols = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"Crossword for {self.quiz.title} ({self.rows}x{self.cols})"

# PUBLIC_INTERFACE
class CrosswordClue(models.Model):
    """Clues for a crossword puzzle."""
    crossword = models.ForeignKey(Crossword, on_delete=models.CASCADE, related_name='clues')
    number = models.PositiveIntegerField()
    direction = models.CharField(max_length=5, choices=(('across','Across'),('down','Down')))
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()
    answer = models.CharField(max_length=64)
    clue = models.TextField()
    points = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('crossword', 'number', 'direction')
        ordering = ['number']

    def __str__(self):
        return f"{self.number} {self.direction}"

# PUBLIC_INTERFACE
class Attempt(models.Model):
    """Represents an attempt by a user on a quiz with time tracking."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'quiz']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({'submitted' if self.is_submitted else 'in-progress'})"

# PUBLIC_INTERFACE
class MCQSubmission(models.Model):
    """Stores user answers for MCQ questions during an attempt."""
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='mcq_submissions')
    question = models.ForeignKey(MCQQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)

    class Meta:
        unique_together = ('attempt', 'question')

# PUBLIC_INTERFACE
class CrosswordAnswer(models.Model):
    """Stores user answers per clue for crosswords."""
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='crossword_answers')
    clue = models.ForeignKey(CrosswordClue, on_delete=models.CASCADE)
    answer = models.CharField(max_length=64, blank=True)
    is_correct = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)

    class Meta:
        unique_together = ('attempt', 'clue')

# PUBLIC_INTERFACE
class LeaderboardEntry(models.Model):
    """Aggregated leaderboard entries, computed on submission."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='leaderboard')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    best_score = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(auto_now=True)
    attempts_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('quiz', 'user')
        ordering = ['-best_score', 'last_attempt_at']

# PUBLIC_INTERFACE
class AuditLog(models.Model):
    """Basic audit trail for admin to view critical actions."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
