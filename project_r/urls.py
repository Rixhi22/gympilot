from django.urls import path, include
from gym.admin import custom_admin_site

urlpatterns = [
    path('superadmin/', custom_admin_site.urls),

    # gym app urls
    path('', include(('gym.urls', 'gym'), namespace='gym')),
]
