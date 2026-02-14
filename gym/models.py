from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# ==========================================
# 🏋️ GYM MODEL (Each Gym Owner)
# ==========================================

class Gym(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="gym",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ==========================================
# 💳 MEMBERSHIP PLAN
# ==========================================

class MembershipPlan(models.Model):
    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE,
        related_name="plans"
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.name} ({self.duration_days} days)"


# ==========================================
# 👥 MEMBER
# ==========================================

class Member(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    join_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('gym', 'phone')  # 🔥 Prevent duplicate phone in same gym

    def __str__(self):
        return f"{self.name} - {self.gym.name}"


# ==========================================
# 🔁 SUBSCRIPTION
# ==========================================
class Subscription(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    member = models.OneToOneField(Member, on_delete=models.CASCADE)  # 🔥 change here
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.name} - {self.plan.name}"

# ==========================================
# 💰 PAYMENT
# ==========================================

class Payment(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.subscription.member.name} - ₹{self.amount}"
