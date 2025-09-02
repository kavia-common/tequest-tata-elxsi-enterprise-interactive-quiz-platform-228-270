#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

Ops note: To bind to the expected deployment port, start with:
    python manage.py runserver 0.0.0.0:3000
"""
import os
import sys


def _maybe_create_admin_user():
    """
    Create a Django superuser automatically if ADMIN_* env vars are present.
    This runs for the runserver/migrate/collectstatic common cases and is safe to call multiple times.
    """
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    # Only proceed if all three are provided
    if not (username and email and password):
        return

    try:
        # Import after settings are configured
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError, ProgrammingError

        User = get_user_model()
        # Avoid duplicate creation; check both username and is_superuser
        exists = User.objects.filter(username=username).exists()
        if not exists:
            # Create the user as superuser
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"[startup] Created Django superuser '{username}' from environment variables.")
        else:
            print(f"[startup] Superuser '{username}' already exists. Skipping creation.")
    except (OperationalError, ProgrammingError):
        # Database may not be migrated yet; ignore silently
        pass
    except Exception as e:
        # Do not crash startup due to admin creation failure; just log
        print(f"[startup] Warning: Failed to auto-create superuser: {e}")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
        # After Django setup, we can optionally create the superuser for common commands
        # Only trigger on commands where DB is/may be ready or soon to be ready.
        if len(sys.argv) >= 2 and sys.argv[1] in {"runserver", "migrate", "makemigrations", "collectstatic"}:
            # We need to setup Django before importing ORM-dependent bits
            try:
                import django
                django.setup()
                _maybe_create_admin_user()
            except Exception as e:
                print(f"[startup] Warning: Skipping auto superuser creation during startup: {e}")
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
