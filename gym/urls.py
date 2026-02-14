from django.urls import path
from .views import (
    dashboard,
    members_list,
    add_member,
    edit_member,
    delete_member,
    renew_subscription,
    plans_list,
    add_plan,
    edit_plan,
    delete_plan,
    payments_list,
    subscriptions_list,
    add_subscription,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('members/', members_list, name='members'),
    path('members/add/', add_member, name='add_member'),
    path('members/edit/<int:member_id>/', edit_member, name='edit_member'),
    path('members/delete/<int:member_id>/', delete_member, name='delete_member'),

    path('plans/', plans_list, name='plans'),
    path('plans/add/', add_plan, name='add_plan'),
    path('plans/edit/<int:plan_id>/', edit_plan, name='edit_plan'),
    path('plans/delete/<int:plan_id>/', delete_plan, name='delete_plan'),

    path('payments/', payments_list, name='payments'),

    # ✅ Subscriptions
    path('subscriptions/', subscriptions_list, name='subscriptions'),
    path('subscriptions/add/', add_subscription, name='add_subscription'),

    path('renew/<int:subscription_id>/', renew_subscription, name='renew_subscription'),
]
