import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the 'dev' admin from DEV_ADMIN_PASSWORD if it doesn't exist."

    def handle(self, *args, **options):
        password = os.environ.get('DEV_ADMIN_PASSWORD')
        if not password:
            self.stdout.write('DEV_ADMIN_PASSWORD is not set; skipping.')
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='dev',
            defaults={'is_staff': True, 'is_superuser': True},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user 'dev'."))
        else:
            self.stdout.write(
                "Admin user 'dev' already exists; nothing changed.")
