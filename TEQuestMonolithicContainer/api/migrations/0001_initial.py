from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('participant', 'Participant'), ('admin', 'Admin')], default='participant', max_length=32)),
                ('display_name', models.CharField(blank=True, max_length=120)),
                ('organization', models.CharField(blank=True, max_length=120)),
                ('bio', models.TextField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('type', models.CharField(choices=[('mcq', 'Multiple Choice'), ('crossword', 'Crossword')], default='mcq', max_length=16)),
                ('is_published', models.BooleanField(default=False)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('time_limit_seconds', models.PositiveIntegerField(default=0, help_text='0 means no limit.')),
                ('max_attempts', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('total_points', models.PositiveIntegerField(default=0)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quizzes_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MCQQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('option_a', models.CharField(max_length=512)),
                ('option_b', models.CharField(max_length=512)),
                ('option_c', models.CharField(blank=True, max_length=512)),
                ('option_d', models.CharField(blank=True, max_length=512)),
                ('correct_option', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=1)),
                ('points', models.PositiveIntegerField(default=1)),
                ('order', models.PositiveIntegerField(default=0)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mcq_questions', to='api.quiz')),
            ],
            options={'ordering': ['order', 'id']},
        ),
        migrations.CreateModel(
            name='Crossword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rows', models.PositiveIntegerField(default=10)),
                ('cols', models.PositiveIntegerField(default=10)),
                ('quiz', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='crossword', to='api.quiz')),
            ],
        ),
        migrations.CreateModel(
            name='CrosswordClue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
                ('direction', models.CharField(choices=[('across', 'Across'), ('down', 'Down')], max_length=5)),
                ('row', models.PositiveIntegerField()),
                ('col', models.PositiveIntegerField()),
                ('answer', models.CharField(max_length=64)),
                ('clue', models.TextField()),
                ('points', models.PositiveIntegerField(default=1)),
                ('crossword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clues', to='api.crossword')),
            ],
            options={'ordering': ['number']},
        ),
        migrations.CreateModel(
            name='Attempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('score', models.IntegerField(default=0)),
                ('is_submitted', models.BooleanField(default=False)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='api.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='attempt',
            index=models.Index(fields=['user', 'quiz'], name='api_attempt_user_id_qui_2a9cde_idx'),
        ),
        migrations.CreateModel(
            name='MCQSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_option', models.CharField(blank=True, max_length=1)),
                ('is_correct', models.BooleanField(default=False)),
                ('points_awarded', models.IntegerField(default=0)),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mcq_submissions', to='api.attempt')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.mcqquestion')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='mcqsubmission',
            unique_together={('attempt', 'question')},
        ),
        migrations.CreateModel(
            name='CrosswordAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(blank=True, max_length=64)),
                ('is_correct', models.BooleanField(default=False)),
                ('points_awarded', models.IntegerField(default=0)),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crossword_answers', to='api.attempt')),
                ('clue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.crosswordclue')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='crosswordanswer',
            unique_together={('attempt', 'clue')},
        ),
        migrations.CreateModel(
            name='LeaderboardEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('best_score', models.IntegerField(default=0)),
                ('last_attempt_at', models.DateTimeField(auto_now=True)),
                ('attempts_count', models.PositiveIntegerField(default=0)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard', to='api.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-best_score', 'last_attempt_at']},
        ),
        migrations.AlterUniqueTogether(
            name='leaderboardentry',
            unique_together={('quiz', 'user')},
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
