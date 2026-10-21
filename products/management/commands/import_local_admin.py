import json
import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Import the local superuser credentials from a protected Render secret file."

    def handle(self, *args, **options):
        fixture_path = Path(
            os.environ.get(
                "MARKETNEST_LOCAL_ADMIN_IMPORT_FILE",
                "/etc/secrets/marketnest-local-admin.json",
            )
        )
        if not fixture_path.is_file():
            self.stdout.write("Protected local admin import file not configured; skipping.")
            return

        try:
            imported = json.loads(fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError("Could not read the protected local admin import file.") from exc

        username = imported.get("username")
        password_hash = imported.get("password")
        if not isinstance(username, str) or not username.strip() or not isinstance(password_hash, str):
            raise CommandError("The protected local admin import file is incomplete.")
        if imported.get("is_superuser") is not True or imported.get("is_staff") is not True:
            raise CommandError("The protected import file must contain a local staff superuser.")
        try:
            identify_hasher(password_hash)
        except (ValueError, TypeError) as exc:
            raise CommandError("The local admin password hash is invalid.") from exc

        User = get_user_model()
        if User.USERNAME_FIELD != "username":
            raise CommandError("This import command expects Django's standard username field.")

        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            user = User(username=username)

        if not user.is_superuser and user.pk:
            raise CommandError(
                "The local admin username already belongs to a non-admin hosted account. "
                "Resolve that account before importing."
            )

        user.password = password_hash
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS("Local admin credentials imported to the hosted database."))
