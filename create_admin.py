import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_r.settings')
django.setup()

from django.contrib.auth.models import User

username = "rishibala"
password = "RIxHI@22"
email = "balarishi213@gmail.com"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("🔥 Superuser created successfully")
else:
    print("ℹ️ Superuser already exists")


