from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('website.urls')),          # public website
    path('app/', include(('gym.urls', 'gym'), namespace='gym')),  # gym system
    path('superadmin/', admin.site.urls),
]
