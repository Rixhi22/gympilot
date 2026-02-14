from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import timedelta
import json

from .models import Payment, Subscription, Gym, Member, MembershipPlan
from .forms import MemberForm, PlanForm, SubscriptionForm


# ======================================================
# 📊 DASHBOARD
# ======================================================

@login_required
def dashboard(request):

    # 🔥 SuperAdmin → redirect to admin panel
    if request.user.is_superuser:
        return redirect('/superadmin/')

    gym = Gym.objects.filter(user=request.user).first()

    if not gym:
        return redirect('owner_login')

    today = timezone.now().date()
    three_days_later = today + timedelta(days=3)

    subscriptions = Subscription.objects.filter(gym=gym)

    # 💰 Total Revenue
    total_revenue = Payment.objects.filter(
        subscription__gym=gym
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    active_members = subscriptions.filter(expiry_date__gt=three_days_later)
    expiring_members = subscriptions.filter(
        expiry_date__range=[today, three_days_later]
    )
    expired_members = subscriptions.filter(expiry_date__lt=today)

    # 📈 Monthly Revenue Chart
    monthly_revenue = (
        Payment.objects
        .filter(subscription__gym=gym)
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    months = []
    totals = []

    for item in monthly_revenue:
        months.append(item['month'].strftime("%b %Y"))
        totals.append(float(item['total']))

    context = {
        'total_revenue': total_revenue,
        'active_count': active_members.count(),
        'expiring_count': expiring_members.count(),
        'expired_count': expired_members.count(),
        'expiring_soon': expiring_members,
        'months': json.dumps(months),
        'totals': json.dumps(totals),
    }

    return render(request, "dashboard.html", context)


# ======================================================
# 👥 MEMBERS
# ======================================================

@login_required
def members_list(request):
    gym = get_object_or_404(Gym, user=request.user)
    members = Member.objects.filter(gym=gym)
    return render(request, "members.html", {"members": members})


@login_required
def add_member(request):
    gym = get_object_or_404(Gym, user=request.user)

    if request.method == "POST":
        form = MemberForm(request.POST, gym=gym)

        if form.is_valid():
            member = form.save(commit=False)
            member.gym = gym
            member.save()
            return redirect("members")
    else:
        form = MemberForm(gym=gym)

    return render(request, "add_member.html", {"form": form})


@login_required
def edit_member(request, member_id):
    gym = get_object_or_404(Gym, user=request.user)
    member = get_object_or_404(Member, id=member_id, gym=gym)

    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect("members")
    else:
        form = MemberForm(instance=member)

    return render(request, "add_member.html", {"form": form})


@login_required
def delete_member(request, member_id):
    gym = get_object_or_404(Gym, user=request.user)
    member = get_object_or_404(Member, id=member_id, gym=gym)

    if request.method == "POST":
        member.delete()

    return redirect("members")


# ======================================================
# 🔁 RENEW SUBSCRIPTION
# ======================================================

@login_required
def renew_subscription(request, subscription_id):
    gym = get_object_or_404(Gym, user=request.user)

    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        gym=gym
    )

    today = timezone.now().date()

    new_start = today if subscription.expiry_date < today else subscription.expiry_date
    new_expiry = new_start + timedelta(days=subscription.plan.duration_days)

    subscription.expiry_date = new_expiry
    subscription.save()

    Payment.objects.create(
        subscription=subscription,
        amount=subscription.plan.price,
        payment_date=today
    )

    return redirect("subscriptions")


# ======================================================
# 💳 PLANS
# ======================================================

@login_required
def plans_list(request):
    gym = get_object_or_404(Gym, user=request.user)
    plans = MembershipPlan.objects.filter(gym=gym)
    return render(request, "plans.html", {"plans": plans})


@login_required
def add_plan(request):
    gym = get_object_or_404(Gym, user=request.user)

    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.gym = gym
            plan.save()
            return redirect("plans")
    else:
        form = PlanForm()

    return render(request, "add_plan.html", {"form": form})


@login_required
def edit_plan(request, plan_id):
    gym = get_object_or_404(Gym, user=request.user)
    plan = get_object_or_404(MembershipPlan, id=plan_id, gym=gym)

    if request.method == "POST":
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect("plans")
    else:
        form = PlanForm(instance=plan)

    return render(request, "add_plan.html", {"form": form})


@login_required
def delete_plan(request, plan_id):
    gym = get_object_or_404(Gym, user=request.user)
    plan = get_object_or_404(MembershipPlan, id=plan_id, gym=gym)
    plan.delete()
    return redirect("plans")


# ======================================================
# 💰 PAYMENTS
# ======================================================

@login_required
def payments_list(request):
    gym = get_object_or_404(Gym, user=request.user)

    payments = Payment.objects.filter(
        subscription__gym=gym
    ).order_by("-payment_date")

    members = Member.objects.filter(gym=gym)

    return render(request, "payments.html", {
        "payments": payments,
        "members": members
    })


# ======================================================
# 📋 SUBSCRIPTIONS LIST
# ======================================================

@login_required
def subscriptions_list(request):

    if request.user.is_superuser:
        return redirect('/superadmin/')

    gym = get_object_or_404(Gym, user=request.user)

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


# ======================================================
# ➕ ADD SUBSCRIPTION
# ======================================================

@login_required
def add_subscription(request):
    gym = get_object_or_404(Gym, user=request.user)

    if request.method == "POST":
        form = SubscriptionForm(request.POST)

        # 🔐 Filter members & plans per gym
        form.fields["member"].queryset = Member.objects.filter(gym=gym)
        form.fields["plan"].queryset = MembershipPlan.objects.filter(gym=gym)

        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.gym = gym
            subscription.save()

            Payment.objects.create(
                subscription=subscription,
                amount=subscription.plan.price,
                payment_date=timezone.now().date()
            )

            return redirect("subscriptions")
    else:
        form = SubscriptionForm()
        form.fields["member"].queryset = Member.objects.filter(gym=gym)
        form.fields["plan"].queryset = MembershipPlan.objects.filter(gym=gym)

    return render(request, "add_subscription.html", {"form": form})


# ======================================================
# 🔐 OWNER LOGIN / LOGOUT
# ======================================================

def owner_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            if Gym.objects.filter(user=user).exists():
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Not a Gym Owner account.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "owner_login.html")


@login_required
def owner_logout(request):
    logout(request)
    return redirect("owner_login")
