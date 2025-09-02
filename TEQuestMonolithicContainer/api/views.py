from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction, models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import (
    UserProfile, Quiz, MCQQuestion, CrosswordClue,
    Attempt, MCQSubmission, CrosswordAnswer, LeaderboardEntry, AuditLog
)
from .serializers import (
    RegistrationSerializer, LoginSerializer, UserSerializer, QuizSerializer,
    AttemptSerializer, MCQSubmissionSerializer, CrosswordAnswerSerializer,
    LeaderboardEntrySerializer
)

def _audit(user, action, metadata=None):
    """Internal helper to record audit logs."""
    AuditLog.objects.create(user=user if user.is_authenticated else None, action=action, metadata=metadata or {})

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health endpoint to verify server availability."""
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user with role and profile details."""
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        _audit(user, 'user_registered', {'username': user.username})
        # Send welcome email (best-effort)
        try:
            send_mail(
                subject='Welcome to TEQuest',
                message=f'Hello {user.username}, welcome to TEQuest!',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=[user.email] if user.email else [],
                fail_silently=True,
            )
        except Exception:
            pass
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint using username and password; uses session auth."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    login(request, user)
    _audit(user, 'user_logged_in', {})
    return Response(UserSerializer(user).data)

# PUBLIC_INTERFACE
@api_view(['POST'])
def logout_view(request):
    """Logout current session."""
    _audit(request.user, 'user_logged_out', {})
    logout(request)
    return Response({'detail': 'Logged out'})

# PUBLIC_INTERFACE
@api_view(['GET', 'PATCH'])
def me(request):
    """Get or update the current user's profile."""
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)
    else:
        profile = getattr(request.user, 'profile', None)
        if profile is None:
            profile = UserProfile.objects.create(user=request.user)
        data = request.data.get('profile', {})
        for field in ['display_name', 'organization', 'bio']:
            if field in data:
                setattr(profile, field, data[field])
        profile.save()
        return Response(UserSerializer(request.user).data)

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def list_quizzes(request):
    """List published and active quizzes."""
    now = timezone.now()
    qs = Quiz.objects.filter(is_published=True).filter(
        models.Q(start_time__lte=now) | models.Q(start_time__isnull=True),
        models.Q(end_time__gte=now) | models.Q(end_time__isnull=True),
    ).order_by('-created_at')
    return Response(QuizSerializer(qs, many=True).data)

# PUBLIC_INTERFACE
@api_view(['GET'])
def my_quizzes(request):
    """List quizzes available to the current user (published/active)."""
    return list_quizzes(request)

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def quiz_detail(request, quiz_id: int):
    """Get quiz details and its questions (public)."""
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_published=True)
    except Quiz.DoesNotExist:
        return Response({'detail': 'Quiz not found'}, status=404)
    return Response(QuizSerializer(quiz).data)

def _can_start_attempt(user: User, quiz: Quiz) -> bool:
    if not quiz.is_active():
        return False
    attempts = Attempt.objects.filter(user=user, quiz=quiz, is_submitted=True).count()
    return attempts < quiz.max_attempts if quiz.max_attempts > 0 else True

# PUBLIC_INTERFACE
@api_view(['POST'])
def start_attempt(request, quiz_id: int):
    """Start an attempt if allowed by time window and attempt limits."""
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_published=True)
    except Quiz.DoesNotExist:
        return Response({'detail': 'Quiz not found'}, status=404)
    if not _can_start_attempt(request.user, quiz):
        return Response({'detail': 'Attempt not allowed'}, status=400)
    attempt = Attempt.objects.create(user=request.user, quiz=quiz)
    _audit(request.user, 'attempt_started', {'quiz_id': quiz.id, 'attempt_id': attempt.id})
    return Response(AttemptSerializer(attempt).data, status=201)

# PUBLIC_INTERFACE
@api_view(['POST'])
def submit_mcq_answer(request, attempt_id: int):
    """Submit or update an MCQ answer within an attempt."""
    try:
        attempt = Attempt.objects.get(id=attempt_id, user=request.user, is_submitted=False)
    except Attempt.DoesNotExist:
        return Response({'detail': 'Active attempt not found'}, status=404)
    serializer = MCQSubmissionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    question = MCQQuestion.objects.get(id=serializer.validated_data['question'].id)
    selected = serializer.validated_data['selected_option']
    if selected not in ('A', 'B', 'C', 'D'):
        return Response({'detail': 'Invalid option'}, status=400)
    is_correct = (selected == question.correct_option)
    points = question.points if is_correct else 0
    sub, _ = MCQSubmission.objects.update_or_create(
        attempt=attempt, question=question,
        defaults={'selected_option': selected, 'is_correct': is_correct, 'points_awarded': points}
    )
    return Response({'is_correct': is_correct, 'points_awarded': points})

# PUBLIC_INTERFACE
@api_view(['POST'])
def submit_crossword_answer(request, attempt_id: int):
    """Submit or update a crossword answer within an attempt."""
    try:
        attempt = Attempt.objects.get(id=attempt_id, user=request.user, is_submitted=False)
    except Attempt.DoesNotExist:
        return Response({'detail': 'Active attempt not found'}, status=404)
    serializer = CrosswordAnswerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    clue = CrosswordClue.objects.get(id=serializer.validated_data['clue'].id)
    answer = serializer.validated_data['answer']
    is_correct = (answer.strip().lower() == clue.answer.strip().lower())
    points = clue.points if is_correct else 0
    obj, _ = CrosswordAnswer.objects.update_or_create(
        attempt=attempt, clue=clue, defaults={'answer': answer, 'is_correct': is_correct, 'points_awarded': points}
    )
    return Response({'is_correct': is_correct, 'points_awarded': points})

def _compute_score(attempt: Attempt) -> int:
    mcq_score = attempt.mcq_submissions.aggregate(s=models.Sum('points_awarded'))['s'] or 0
    cw_score = attempt.crossword_answers.aggregate(s=models.Sum('points_awarded'))['s'] or 0
    return int(mcq_score + cw_score)

# PUBLIC_INTERFACE
@api_view(['POST'])
def finalize_attempt(request, attempt_id: int):
    """Finalize an attempt, compute score, update leaderboard and send email."""
    try:
        with transaction.atomic():
            attempt = Attempt.objects.select_for_update().get(id=attempt_id, user=request.user, is_submitted=False)
            attempt.ended_at = timezone.now()
            attempt.score = _compute_score(attempt)
            attempt.is_submitted = True
            attempt.save()

            lb, created = LeaderboardEntry.objects.get_or_create(quiz=attempt.quiz, user=request.user)
            lb.best_score = max(lb.best_score, attempt.score if attempt.score is not None else 0)
            lb.attempts_count = Attempt.objects.filter(user=request.user, quiz=attempt.quiz, is_submitted=True).count()
            lb.save()

            _audit(request.user, 'attempt_finalized', {'quiz_id': attempt.quiz.id, 'attempt_id': attempt.id, 'score': attempt.score})

        # Send email notification (best-effort)
        try:
            if request.user.email:
                send_mail(
                    subject=f'Attempt submitted: {attempt.quiz.title}',
                    message=f'Your score: {attempt.score}',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
        except Exception:
            pass

        return Response({'score': attempt.score})
    except Attempt.DoesNotExist:
        return Response({'detail': 'Active attempt not found'}, status=404)

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request, quiz_id: int):
    """Leaderboard for a given quiz."""
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({'detail': 'Quiz not found'}, status=404)
    entries = LeaderboardEntry.objects.filter(quiz=quiz).order_by('-best_score', 'last_attempt_at')[:100]
    return Response(LeaderboardEntrySerializer(entries, many=True).data)

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Initiate a password reset email with a basic token link."""
    email = request.data.get('email', '').strip().lower()
    if not email:
        return Response({'detail': 'Email required'}, status=400)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Avoid leaking user existence
        return Response({'detail': 'If the email exists, a reset link will be sent.'})

    # Use Django's built in password reset token generator
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    base = getattr(settings, 'SITE_URL', 'http://localhost:3000')
    path = getattr(settings, 'PASSWORD_RESET_PATH', '/reset-password')
    reset_link = f"{base.rstrip('/')}{path}?uid={uidb64}&token={token}"

    try:
        send_mail(
            subject='Password Reset - TEQuest',
            message=f"Click the link to reset your password: {reset_link}",
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        pass

    _audit(user, 'password_reset_requested', {})
    return Response({'detail': 'If the email exists, a reset link will be sent.'})

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """Confirm password reset given uid/token and new password."""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    if not uid or not token or not new_password:
        return Response({'detail': 'Missing fields'}, status=400)
    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
    except Exception:
        return Response({'detail': 'Invalid link'}, status=400)
    if not default_token_generator.check_token(user, token):
        return Response({'detail': 'Invalid token'}, status=400)
    user.set_password(new_password)
    user.save()
    _audit(user, 'password_reset_confirmed', {})
    return Response({'detail': 'Password updated'})

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_stats(request):
    """Admin analytics summary."""
    return Response({
        'users': User.objects.count(),
        'quizzes': Quiz.objects.count(),
        'attempts': Attempt.objects.count(),
        'submissions_mcq': MCQSubmission.objects.count(),
        'submissions_crossword': CrosswordAnswer.objects.count(),
        'leaderboard_entries': LeaderboardEntry.objects.count(),
    })

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([IsAdminUser])
def audit_logs(request):
    """Admin audit logs viewer."""
    logs = AuditLog.objects.all()[:500]
    return Response([{
        'id': log.id,
        'user': log.user.username if log.user else None,
        'action': log.action,
        'metadata': log.metadata,
        'created_at': log.created_at,
    } for log in logs])
