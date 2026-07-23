from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from pathlib import Path


class Command(BaseCommand):
    help = "Load quiz data into PostgreSQL"

    def handle(self, *args, **kwargs):
        fixture = Path("quiz_data.json")

        if fixture.exists():
            self.stdout.write("Loading quiz_data.json...")
            call_command("loaddata", str(fixture))
            self.stdout.write(self.style.SUCCESS("Quiz data imported successfully."))
        else:
            self.stdout.write(self.style.ERROR("quiz_data.json not found."))

        User = get_user_model()

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123"
            )
            self.stdout.write(self.style.SUCCESS("Superuser created."))
        else:
            self.stdout.write("Superuser already exists.")