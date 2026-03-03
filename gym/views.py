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
from django.db import IntegrityError, transaction
from .forms import MemberForm, PlanForm, SubscriptionForm
from .models import Subscription, Gym, Member, MembershipPlan, Payment
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
    total_revenue = Subscription.objects.filter(
    gym=gym
    ).aggregate(total=Sum('amount_paid'))['total'] or Decimal("0.00")
    active_members = subscriptions.filter(expiry_date__gt=three_days_later)
    expiring_members = subscriptions.filter(expiry_date__range=[today, three_days_later])
    expired_members = subscriptions.filter(expiry_date__lt=today)

    # MONTHLY REVENUE
    monthly_revenue = (
    Subscription.objects
    .filter(gym=gym)
    .annotate(month=TruncMonth('paid_on'))
    .values('month')
    .annotate(total=Sum('amount_paid'))
    .order_by('month')
)

    months = []
    totals = []

    for item in monthly_revenue:
        if item['month']:
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
    today = timezone.now().date()

    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        form.fields["member"].queryset = Member.objects.filter(gym=gym)
        form.fields["plan"].queryset = MembershipPlan.objects.filter(gym=gym)

        if form.is_valid():
            data = form.cleaned_data
            member = data["member"]
            plan = data["plan"]

            active_subscription = Subscription.objects.filter(
                gym=gym,
                member=member,
                expiry_date__gte=today
            ).first()

            if active_subscription and not request.POST.get("force_expire"):
                return render(request, "confirm_replace.html", {
                    "form": form,
                    "active_subscription": active_subscription
                })

            if active_subscription:
                active_subscription.expiry_date = today - timedelta(days=1)
                active_subscription.expiry_reason = "replaced"
                active_subscription.save()

            Subscription.objects.create(
                gym=gym,
                member=member,
                plan=plan,
                start_date=data["start_date"],                extra_months=data["extra_months"],
                discount_percent=data["discount_percent"],
                personal_training_fee=data["personal_training_fee"],
                payment_mode=data["payment_mode"],
                paid_on=today
            )

            messages.success(request, "Subscription created successfully!")
            return redirect("gym:subscriptions")

    else:
        member_id = request.GET.get("member")
        plan_id = request.GET.get("plan")
        extra = request.GET.get("extra")
        discount = request.GET.get("discount")
        pt = request.GET.get("pt")

        initial_data = {}

        if member_id:
            initial_data["member"] = member_id
        if plan_id:
            initial_data["plan"] = plan_id
        if extra:
            initial_data["extra_months"] = extra
        if discount:
            initial_data["discount_percent"] = discount
        if pt:
            initial_data["personal_training_fee"] = pt

        form = SubscriptionForm(initial=initial_data)
        form.fields["member"].queryset = Member.objects.filter(gym=gym)
        form.fields["plan"].queryset = MembershipPlan.objects.filter(gym=gym)

    return render(request, "add_subscription.html", {"form": form})



# RENEW SUBSCRIPTION
@login_required
def renew_subscription(request, subscription_id):
    gym = get_object_or_404(Gym, owner=request.user)
    old_subscription = get_object_or_404(Subscription, id=subscription_id, gym=gym)

    today = timezone.now().date()

    if old_subscription.expiry_date >= today:
        messages.error(request, "This subscription is still active.")
        return redirect("gym:subscriptions")

    return redirect(
        f"/app/add-subscription/?member={old_subscription.member.id}"
        f"&plan={old_subscription.plan.id}"
        f"&extra={old_subscription.extra_months}"
        f"&discount={old_subscription.discount_percent}"
        f"&pt={old_subscription.personal_training_fee}"
    )
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

from .utils.export_excel import export_gym_data

@login_required
def download_my_gym_data(request):
    gym = get_object_or_404(Gym, owner=request.user)
    return export_gym_data(gym)