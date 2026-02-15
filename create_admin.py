import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_r.settings')
django.setup()

from django.contrib.auth.models import User

USERNAME = "admin"
EMAIL = "admin@gympilot.com"
PASSWORD = "admin123"

if not User.objects.filter(username=USERNAME).exists():
    print("Creating admin user...")
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
else:
    print("Admin user already exists.")
