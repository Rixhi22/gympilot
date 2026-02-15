import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_r.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from gym.models import Gym

print("----- RESETTING DATABASE USERS -----")

# Delete all sessions (important)
Session.objects.all().delete()

# Delete all users
User.objects.all().delete()

# Delete gym owners (if linked)
Gym.objects.all().delete()

print("Old users cleared")

# Create fresh admin
username = "admin"
password = "admin123"
email = "balarishi213@gmail.com"

User.objects.create_superuser(username, email, password)

print("New admin created successfully!")
