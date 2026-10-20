import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the preview superuser from private environment variables, if configured."

    def handle(self, *args, **options):
        username = os.environ.get("MARKETNEST_ADMIN_USERNAME", "").strip()
        password = os.environ.get("MARKETNEST_ADMIN_PASSWORD", "")

        if not username and not password:
            self.stdout.write("Admin bootstrap not configured; skipping.")
            return
        if not username or not password:
            raise CommandError(
                "Set both MARKETNEST_ADMIN_USERNAME and MARKETNEST_ADMIN_PASSWORD in the service environment."
            )

        User = get_user_model()
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            User.objects.create_superuser(
                username=username,
                email=os.environ.get("MARKETNEST_ADMIN_EMAIL", "").strip(),
                password=password,
            )
            self.stdout.write(self.style.SUCCESS("Preview admin account created."))
            return

        if not user.is_superuser:
            raise CommandError(
                "That username already belongs to a regular account. Choose a separate admin username."
            )
        self.stdout.write("Preview admin account already exists; no changes made.")
