from django.core.management.base import BaseCommand
from gym.reminder import send_expiry_reminders


class Command(BaseCommand):
    help = "Send WhatsApp reminders for expiring memberships"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Do not send messages; only print what would be sent.'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        send_expiry_reminders(dry_run=dry_run)
        self.stdout.write(self.style.SUCCESS("Reminders processed successfully!"))
