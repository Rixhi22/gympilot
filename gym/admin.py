from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from django.urls import reverse
from .models import Gym, MembershipPlan, Member, Subscription, Payment


# ============================================
# CUSTOM ADMIN SITE - SUPERUSER ONLY ACCESS
# ============================================

class SuperAdminOnly(AdminSite):
    """
    Custom AdminSite that only allows superusers to access.
    Regular gym owners cannot access admin portal even if they have a valid session.
    """
    site_header = "GymPilot Control Panel"
    site_title = "GymPilot Admin"
    index_title = "Welcome to GymPilot SuperAdmin"
    
    def has_permission(self, request):
        """
        Only superusers can access the admin site.
        Regular users (even if logged in to gym portal) are redirected.
        """
        return request.user and request.user.is_active and request.user.is_superuser
    
    def redirect_to_login(self, path, extra_get_params=None):
        """
        Redirect non-superusers to gym login page.
        """
        return redirect('gym:owner_login')


# Create custom admin site instance
custom_admin_site = SuperAdminOnly(name='admin')

# Register models with custom admin site
custom_admin_site.register(Gym)
custom_admin_site.register(MembershipPlan)
custom_admin_site.register(Member)
custom_admin_site.register(Subscription)
custom_admin_site.register(Payment)
