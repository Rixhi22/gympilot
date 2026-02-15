from django.apps import AppConfig

class GymConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gym'

    def ready(self):
        import os
        from django.contrib.auth.models import User

        # Only run on server
        if os.environ.get('RENDER'):
            if not User.objects.filter(username='rishi').exists():
                User.objects.create_superuser(
                    username='rishibala',
                    email='balarishi213@gmail.com',
                    password='RIxHI@22'
                )
                print("🔥 Default admin created: rishibala / RIxHI@22")
