from django.db import models
from django.contrib.auth.models import User

# Import custom user for owner reference
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from datetime import date
from django.core.validators import RegexValidator


# ===============================
# GYM (each owner has one gym)
# ===============================
class Gym(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


# ===============================
# MEMBER
# ===============================
class Member(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    country_code = models.CharField(max_length=5, default="+91")
    phone = models.CharField(max_length=10)

    # ⭐ NEW FIELD
    join_date = models.DateField(default=timezone.now)
   
    phone_validator = RegexValidator(r'^[6-9]\d{9}$', 'Enter valid Indian mobile number')

    phone = models.CharField(max_length=10, validators=[phone_validator])
    def full_phone(self):
        return f"{self.country_code}{self.phone}"

    def __str__(self):
        return self.name


# ===============================
# MEMBERSHIP PLAN
# ===============================
class MembershipPlan(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_months = models.IntegerField()

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


# ===============================
# SUBSCRIPTION
# ===============================
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

class Subscription(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)

    # IMPORTANT FIX
    start_date = models.DateField(default=timezone.localdate)
    expiry_date = models.DateField(blank=True, null=True)

    extra_months = models.IntegerField(default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    personal_training_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    member_code = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)

 


    # ---------------- PRICE CALCULATION ----------------
    def calculate_amount(self):
        base_price = Decimal(self.plan.price)

        # Extra months extend duration but are offered free of cost.
        # Do NOT increase the base price for `extra_months`.

        # discount
        discount_amount = base_price * (Decimal(self.discount_percent) / Decimal('100'))
        discounted_price = base_price - discount_amount

        # final
        self.final_amount = discounted_price + Decimal(self.personal_training_fee)

    # ---------------- SAVE ----------------
    def save(self, *args, **kwargs):
        if not self.member_code:
            last = Subscription.objects.order_by('-id').first()

            if last and last.member_code:
                last_number = int(last.member_code.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.member_code = f"GP-{new_number:04d}"

        super().save(*args, **kwargs)



# ===============================
# PAYMENT
# ===============================
class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=date.today)
    payment_method = models.CharField(max_length=50, default="Cash")
    billing_start = models.DateField(null=True, blank=True)
    billing_end = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.subscription.member} - ₹{self.amount_paid}"
