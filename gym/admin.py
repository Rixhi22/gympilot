from django.contrib import admin
from .models import Gym, MembershipPlan, Member, Subscription, Trainer

admin.site.register(Gym)
admin.site.register(Member)
admin.site.register(MembershipPlan)
admin.site.register(Subscription)
admin.site.register(Trainer)

