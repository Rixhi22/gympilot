from django.contrib import admin
from .models import Gym, MembershipPlan, Member, Subscription, Payment

admin.site.register(Gym)
admin.site.register(MembershipPlan)
admin.site.register(Member)
admin.site.register(Subscription)
admin.site.register(Payment)
