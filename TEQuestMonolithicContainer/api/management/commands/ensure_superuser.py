import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

# PUBLIC_INTERFACE
class Command(BaseCommand):
    """Management command to create a Django superuser using ADMIN_* env vars if not present."""

    help = "Create a superuser from env vars ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD if it doesn't exist."

    def handle(self, *args, **options):
        """
        Reads ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD from environment.
        If all are present and the user does not exist, creates a superuser.
        This command is idempotent.
        """
        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        if not (username and email and password):
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD must all be set. "
                "Skipping superuser creation."
            ))
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists. Nothing to do."))
            return

        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}' from environment variables."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create superuser: {e}"))
