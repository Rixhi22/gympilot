from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import json

from .models import Payment, Subscription, Gym, Member, MembershipPlan
from .forms import MemberForm, PlanForm, SubscriptionForm


# ================= OWNER LOGIN =================

def owner_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            if Gym.objects.filter(owner=user).exists():
                login(request, user)
                return redirect("/app/")
            else:
                messages.error(request, "Not a Gym Owner account.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "owner_login.html")


@login_required
def owner_logout(request):
    logout(request)
    return redirect("gym:owner_login")


# ================= DASHBOARD =================

@login_required
def dashboard(request):
    # If the user is a Django superuser but also owns a Gym, allow access
    # to the gym dashboard. Only redirect to the Django admin when the
    # superuser does NOT own any Gym entry.
    if request.user.is_superuser and not Gym.objects.filter(owner=request.user).exists():
        return redirect('/superadmin/')

    gym = get_object_or_404(Gym, owner=request.user)

    today = timezone.now().date()
    three_days_later = today + timedelta(days=3)

    subscriptions = Subscription.objects.filter(gym=gym)

    # TOTAL REVENUE
    total_revenue = Payment.objects.filter(
        subscription__gym=gym
    ).aggregate(total=Sum('amount_paid'))['total'] or Decimal("0.00")

    active_members = subscriptions.filter(expiry_date__gt=three_days_later)
    expiring_members = subscriptions.filter(expiry_date__range=[today, three_days_later])
    expired_members = subscriptions.filter(expiry_date__lt=today)

    # MONTHLY REVENUE
    monthly_revenue = (
        Payment.objects
        .filter(subscription__gym=gym)
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount_paid'))
        .order_by('month')
    )

    months = []
    totals = []

    for item in monthly_revenue:
        months.append(item['month'].strftime("%b %Y"))
        totals.append(float(item['total'] or 0))

    context = {
        'total_revenue': total_revenue,
        'active_count': active_members.count(),
        'expiring_count': expiring_members.count(),
        'expired_count': expired_members.count(),
        'expiring_soon': expiring_members,
        'today': today,
        'today_plus_3': three_days_later,
        'months': json.dumps(months),
        'totals': json.dumps(totals),
    }

    return render(request, "dashboard.html", context)


# ================= MEMBERS =================

@login_required
def members_list(request):
    gym = Gym.objects.filter(owner=request.user).first()
    if not gym:
                return redirect('gym:dashboard')
    members = Member.objects.filter(gym=gym).order_by("-id")
    return render(request, "members.html", {"members": members})


@login_required
def add_member(request):
    gym = get_object_or_404(Gym, owner=request.user)

    if request.method == "POST":
        form = MemberForm(request.POST, gym=gym)
        if form.is_valid():
            member = form.save(commit=False)
            member.gym = gym
            member.save()
            return redirect("gym:members")
    else:
        form = MemberForm(gym=gym)

    return render(request, "add_member.html", {"form": form})


@login_required
def edit_member(request, member_id):
    gym = get_object_or_404(Gym, owner=request.user)
    member = get_object_or_404(Member, id=member_id, gym=gym)

    if request.method == "POST":
        form = MemberForm(request.POST, instance=member, gym=gym)
        if form.is_valid():
            form.save()
            return redirect("gym:members")
    else:
        form = MemberForm(instance=member, gym=gym)

    return render(request, "add_member.html", {"form": form})


@login_required
def delete_member(request, member_id):
    gym = get_object_or_404(Gym, owner=request.user)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    member.delete()
    return redirect("gym:members")


# ================= PLANS =================

@login_required
def plans_list(request):
    gym = get_object_or_404(Gym, owner=request.user)
    plans = MembershipPlan.objects.filter(gym=gym)
    return render(request, "plans.html", {"plans": plans})


@login_required
def add_plan(request):
    gym = get_object_or_404(Gym, owner=request.user)

    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.gym = gym
            plan.save()
            return redirect("gym:plans")
    else:
        form = PlanForm()

    return render(request, "add_plan.html", {"form": form})


@login_required
def edit_plan(request, plan_id):
    gym = get_object_or_404(Gym, owner=request.user)
    plan = get_object_or_404(MembershipPlan, id=plan_id, gym=gym)

    if request.method == "POST":
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect("gym:plans")
    else:
        form = PlanForm(instance=plan)

    return render(request, "add_plan.html", {"form": form})


@login_required
def delete_plan(request, plan_id):
    gym = get_object_or_404(Gym, owner=request.user)
    plan = get_object_or_404(MembershipPlan, id=plan_id, gym=gym)
    plan.delete()
    return redirect("gym:plans")


# ================= PAYMENTS =================

@login_required
def payments_list(request):
    gym = get_object_or_404(Gym, owner=request.user)

    payments = Payment.objects.filter(
        subscription__gym=gym
    ).order_by("-payment_date")

    return render(request, "payments.html", {"payments": payments})


# ================= SUBSCRIPTIONS =================

@login_required
def subscriptions_list(request):
    gym = get_object_or_404(Gym, owner=request.user)

    subscriptions = Subscription.objects.filter(
        gym=gym
    ).select_related("member", "plan")

    today = timezone.now().date()
    today_plus_3 = today + timedelta(days=3)

    return render(request, "subscriptions.html", {
        "subscriptions": subscriptions,
        "today": today,
        "today_plus_3": today_plus_3,
    })


# ADD SUBSCRIPTION
@login_required
def add_subscription(request):
    gym = get_object_or_404(Gym, owner=request.user)

    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        form.fields["member"].queryset = Member.objects.filter(gym=gym)
        form.fields["plan"].queryset = MembershipPlan.objects.filter(gym=gym)

        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.gym = gym

            today = timezone.now().date()

# subscription always starts today
            subscription.start_date = today

# calculate expiry from plan duration
            total_months = subscription.plan.duration_months + subscription.extra_months
            subscription.expiry_date = today + relativedelta(months=total_months)

            subscription.save()


            # AUTO CREATE PAYMENT
            Payment.objects.create(
                subscription=subscription,
                amount_paid=subscription.final_amount,
                payment_date=timezone.now().date(),
                payment_method="Cash"
            )

            messages.success(request, "Subscription added successfully!")
            return redirect("gym:subscriptions")

    else:
        form = SubscriptionForm()
        form.fields["member"].queryset = Member.objects.filter(gym=gym)
        form.fields["plan"].queryset = MembershipPlan.objects.filter(gym=gym)

    return render(request, "add_subscription.html", {"form": form})


# RENEW SUBSCRIPTION
@login_required
def renew_subscription(request, subscription_id):
    gym = get_object_or_404(Gym, owner=request.user)
    subscription = get_object_or_404(Subscription, id=subscription_id, gym=gym)

    today = timezone.now().date()

    if subscription.expiry_date < today:
        new_start = today
    else:
        new_start = subscription.expiry_date

    total_months = subscription.plan.duration_months + subscription.extra_months
    new_expiry = new_start + relativedelta(months=total_months)

    subscription.start_date = new_start
    subscription.expiry_date = new_expiry
    subscription.save()

    Payment.objects.create(
        subscription=subscription,
        amount_paid=subscription.final_amount,
        payment_date=today,
        payment_method="Cash",
        billing_start=new_start,
    billing_end=new_expiry
    )

    messages.success(request, "Membership renewed successfully!")
    return redirect("gym:subscriptions")

# ================= EDIT SUBSCRIPTION =================
@login_required
def edit_subscription(request, sub_id):
    gym = get_object_or_404(Gym, owner=request.user)
    subscription = get_object_or_404(Subscription, id=sub_id, gym=gym)

    if request.method == "POST":
        form = SubscriptionForm(request.POST, instance=subscription)

        form.fields["member"].queryset = Member.objects.filter(gym=gym)
        form.fields["plan"].queryset = MembershipPlan.objects.filter(gym=gym)

        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.gym = gym
            subscription.save()

            messages.success(request, "Subscription updated successfully!")
            return redirect("gym:subscriptions")

    else:
        form = SubscriptionForm(instance=subscription)
        form.fields["member"].queryset = Member.objects.filter(gym=gym)
        form.fields["plan"].queryset = MembershipPlan.objects.filter(gym=gym)

    return render(request, "add_subscription.html", {"form": form})


# AJAX PLAN DETAILS
@login_required
def plan_details(request, plan_id):
    gym = get_object_or_404(Gym, owner=request.user)
    plan = get_object_or_404(MembershipPlan, id=plan_id, gym=gym)

    today = timezone.now().date()
    expiry = today + relativedelta(months=plan.duration_months)

    return JsonResponse({
        "price": float(plan.price),
        "duration": plan.duration_months,
        "expiry": expiry.strftime("%d %b %Y"),
    })

# ================= DELETE SUBSCRIPTION =================
@login_required
def delete_subscription(request, sub_id):
    gym = get_object_or_404(Gym, owner=request.user)
    subscription = get_object_or_404(Subscription, id=sub_id, gym=gym)

    if request.method == "POST":
        subscription.delete()
        messages.success(request, "Subscription deleted successfully!")

    return redirect("gym:subscriptions")
