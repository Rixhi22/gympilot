from django.utils import timezone
from datetime import timedelta
from gym.models import Subscription
#from gym.whatsapp import send_whatsapp_message


def send_expiry_reminders(dry_run: bool = False):
    """Send WhatsApp reminders for subscriptions expiring today/soon.

    If `dry_run` is True, messages will not be sent to Twilio; instead the
    function will print the phone and message that would be sent.
    """

    today = timezone.now().date()

    # Remind 3 days before expiry (0 == today)
    reminder_days = [0, 1, 2, 3]

    for days in reminder_days:
        target_date = today + timedelta(days=days)

        expiring_subs = Subscription.objects.filter(expiry_date=target_date)

        for sub in expiring_subs:
            member = sub.member
            phone = member.full_phone() if hasattr(member, 'full_phone') else None

            if not phone:
                print(f"Skipping {member} — no phone available")
                continue

            # Ensure country code
            if not phone.startswith("+"):
                phone = "+91" + phone

            if days == 0:
                msg_type = "TODAY"
            elif days == 1:
                msg_type = "TOMORROW"
            else:
                msg_type = f"in {days} days"

            message = (
                f"🏋️ GymPilot Membership Alert\n\n"
                f"Hi {member.name},\n\n"
                f"Your gym membership expires {msg_type}.\n"
                f"Expiry Date: {sub.expiry_date}\n\n"
                f"Please renew to avoid interruption 💪\n\n"
                f"— {sub.gym.name}"
            )

            if dry_run:
                print("--- DRY RUN: would send ---")
                print(f"To: {phone}")
                print(message)
                print("--- end ---\n")
                continue

            try:
                send_whatsapp_message(phone, message)
                print(f"Sent to {member.name} ({phone})")
            except Exception as e:
                print(f"FAILED {member.name}: {e}")
