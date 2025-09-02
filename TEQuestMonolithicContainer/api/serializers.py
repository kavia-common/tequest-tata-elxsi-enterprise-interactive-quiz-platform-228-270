from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    UserProfile, Quiz, MCQQuestion, Crossword, CrosswordClue,
    Attempt, MCQSubmission, CrosswordAnswer, LeaderboardEntry
)

# PUBLIC_INTERFACE
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with role exposure."""
    class Meta:
        model = UserProfile
        fields = ['role', 'display_name', 'organization', 'bio']

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Serializer for user with nested profile."""
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

# PUBLIC_INTERFACE
class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('participant','Participant'),('admin','Admin')], default='participant')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role', 'participant')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, role=role)
        return user

# PUBLIC_INTERFACE
class LoginSerializer(serializers.Serializer):
    """Login serializer for username/password authentication."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# PUBLIC_INTERFACE
class MCQQuestionSerializer(serializers.ModelSerializer):
    """Serializer for MCQ question."""
    class Meta:
        model = MCQQuestion
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'points', 'order']

# PUBLIC_INTERFACE
class CrosswordClueSerializer(serializers.ModelSerializer):
    """Serializer for crossword clues."""
    class Meta:
        model = CrosswordClue
        fields = ['id', 'number', 'direction', 'row', 'col', 'clue', 'points', 'answer']
        extra_kwargs = {
            'answer': {'write_only': True}  # hide real answer from participants
        }

# PUBLIC_INTERFACE
class CrosswordSerializer(serializers.ModelSerializer):
    """Serializer for crossword puzzle."""
    clues = CrosswordClueSerializer(many=True, read_only=True)

    class Meta:
        model = Crossword
        fields = ['rows', 'cols', 'clues']

# PUBLIC_INTERFACE
class QuizSerializer(serializers.ModelSerializer):
    """Serializer for quiz details with nested question data."""
    mcq_questions = MCQQuestionSerializer(many=True, read_only=True)
    crossword = CrosswordSerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'type', 'is_published',
            'start_time', 'end_time', 'time_limit_seconds',
            'max_attempts', 'total_points', 'mcq_questions', 'crossword'
        ]

# PUBLIC_INTERFACE
class AttemptSerializer(serializers.ModelSerializer):
    """Attempt serializer with minimal fields."""
    class Meta:
        model = Attempt
        fields = ['id', 'quiz', 'started_at', 'ended_at', 'score', 'is_submitted']

# PUBLIC_INTERFACE
class MCQSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for MCQ answer submission."""
    class Meta:
        model = MCQSubmission
        fields = ['question', 'selected_option']

# PUBLIC_INTERFACE
class CrosswordAnswerSerializer(serializers.ModelSerializer):
    """Serializer for crossword answer submission."""
    class Meta:
        model = CrosswordAnswer
        fields = ['clue', 'answer']

# PUBLIC_INTERFACE
class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """Leaderboard serializer exposing user and score."""
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'display_name': getattr(obj.user.profile, 'display_name', '') if hasattr(obj.user, 'profile') else ''
        }

    class Meta:
        model = LeaderboardEntry
        fields = ['user', 'best_score', 'attempts_count', 'last_attempt_at']
