from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('superadmin/', admin.site.urls),

    # gym app urls
path('', include(('gym.urls', 'gym'), namespace='gym')),
]
