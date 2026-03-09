from django.contrib import admin
from .models import MembershipPlan, Member, Subscription, Trainer

admin.site.register(Member)
admin.site.register(MembershipPlan)
admin.site.register(Subscription)
admin.site.register(Trainer)
