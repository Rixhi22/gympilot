from django.contrib import admin
from django.urls import path, include
from gym.views import owner_login, owner_logout

urlpatterns = [
    # Django SuperAdmin
    path('superadmin/', admin.site.urls),

    # Gym Owner Auth
    path('login/', owner_login, name='owner_login'),
    path('logout/', owner_logout, name='owner_logout'),

    # Gym App URLs
    path('', include('gym.urls')),
]
