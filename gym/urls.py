from django.urls import path
from . import views

app_name = "gym"

urlpatterns = [

    # AUTH
    path('login/', views.owner_login, name='owner_login'),
    path('logout/', views.owner_logout, name='owner_logout'),

    # DASHBOARD
    path('', views.dashboard, name='dashboard'),

    # MEMBERS
    path('members/', views.members_list, name='members'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/edit/<int:member_id>/', views.edit_member, name='edit_member'),
    path('members/delete/<int:member_id>/', views.delete_member, name='delete_member'),

    # PLANS
    path('plans/', views.plans_list, name='plans'),
    path('plans/add/', views.add_plan, name='add_plan'),
    path('plans/edit/<int:plan_id>/', views.edit_plan, name='edit_plan'),
    path('plans/delete/<int:plan_id>/', views.delete_plan, name='delete_plan'),

    # SUBSCRIPTIONS
    path('subscriptions/', views.subscriptions_list, name='subscriptions'),
    path('subscriptions/add/', views.add_subscription, name='add_subscription'),

    # ⭐⭐⭐ THIS WAS THE MISSING / BROKEN PART
    path('subscriptions/edit/<int:sub_id>/', views.edit_subscription, name='edit_subscription'),
    path('subscriptions/delete/<int:sub_id>/', views.delete_subscription, name='delete_subscription'),
    path('subscriptions/renew/<int:subscription_id>/', views.renew_subscription, name='renew_subscription'),

    # AJAX PLAN
    path('plan-details/<int:plan_id>/', views.plan_details, name='plan_details'),

    path('export-data/', views.download_my_gym_data, name='export_data'),
]