from django.core.management.base import BaseCommand
from django.conf import settings
from gym.models import Gym, Member, MembershipPlan, Subscription, Payment, Trainer
import pandas as pd
import os
from datetime import datetime


class Command(BaseCommand):
    help = "Backup Gym Data to Excel"

    def handle(self, *args, **kwargs):

        # ---------------- GYMS ----------------
        gyms_data = []
        for g in Gym.objects.select_related("owner"):
            gyms_data.append({
                "Gym Name": g.name,
                "Owner": g.owner.username
            })

        gyms_df = pd.DataFrame(gyms_data)
        if not gyms_df.empty:
            gyms_df.insert(0, "S.No", range(1, len(gyms_df) + 1))


        # ---------------- MEMBERS ----------------
        members_data = []
        for m in Member.objects.select_related("gym"):
            members_data.append({
                "Name": m.name,
                "Phone": m.full_phone(),
                "Gender": m.gender,
                "Age": m.age,
                "Join Date": m.join_date,
                "Gym": m.gym.name
            })

        members_df = pd.DataFrame(members_data)
        if not members_df.empty:
            members_df.insert(0, "S.No", range(1, len(members_df) + 1))


        # ---------------- PLANS ----------------
        plans_data = []
        for p in MembershipPlan.objects.select_related("gym"):
            plans_data.append({
                "Plan": p.name,
                "Price": float(p.price),
                "Duration Months": p.duration_months,
                "Gym": p.gym.name
            })

        plans_df = pd.DataFrame(plans_data)
        if not plans_df.empty:
            plans_df.insert(0, "S.No", range(1, len(plans_df) + 1))


        # ---------------- SUBSCRIPTIONS ----------------
        subscriptions_data = []

        subs = Subscription.objects.select_related("member", "plan", "gym")

        for s in subs:
            subscriptions_data.append({
                "Member Code": s.member_code,
                "Member": s.member.name,
                "Plan": s.plan.name,
                "Start Date": s.start_date,
                "Expiry Date": s.expiry_date,
                "Extra Months": s.extra_months,
                "Discount %": float(s.discount_percent),
                "Personal Training Fee": float(s.personal_training_fee),
                "Final Amount": float(s.final_amount),
                "Paid Amount": float(s.amount_paid),
                "Payment Mode": s.payment_mode,
                "Paid On": s.paid_on,
                "Gym": s.gym.name
            })

        subscriptions_df = pd.DataFrame(subscriptions_data)
        if not subscriptions_df.empty:
            subscriptions_df.insert(0, "S.No", range(1, len(subscriptions_df) + 1))


        # ---------------- PAYMENTS ----------------
        payments_data = []

        payments = Payment.objects.select_related(
            "subscription",
            "subscription__member",
            "subscription__plan"
        )

        for p in payments:
            payments_data.append({
                "Member": p.subscription.member.name,
                "Plan": p.subscription.plan.name,
                "Amount": float(p.amount_paid),
                "Payment Method": p.payment_method,
                "Payment Date": p.payment_date,
                "Billing Start": p.billing_start,
                "Billing End": p.billing_end
            })

        payments_df = pd.DataFrame(payments_data)
        if not payments_df.empty:
            payments_df.insert(0, "S.No", range(1, len(payments_df) + 1))


        # ---------------- TRAINERS ----------------
        trainers_data = []

        for t in Trainer.objects.select_related("gym"):
            trainers_data.append({
                "Trainer Code": t.trainer_code,
                "Name": t.name,
                "Phone": t.phone,
                "Gender": t.gender,
                "Experience Years": t.experience_years,
                "Salary": float(t.salary),
                "Join Date": t.join_date,
                "Shift Start": t.shift_start,
                "Shift End": t.shift_end,
                "Gym": t.gym.name
            })

        trainers_df = pd.DataFrame(trainers_data)
        if not trainers_df.empty:
            trainers_df.insert(0, "S.No", range(1, len(trainers_df) + 1))


        # ---------------- FILE LOCATION ----------------
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        filename = os.path.join(backup_dir, f"gym_backup_{now}.xlsx")


        # ---------------- WRITE EXCEL ----------------
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:

            gyms_df.to_excel(writer, sheet_name="Gyms", index=False)
            members_df.to_excel(writer, sheet_name="Members", index=False)
            plans_df.to_excel(writer, sheet_name="Plans", index=False)
            subscriptions_df.to_excel(writer, sheet_name="Subscriptions", index=False)
            payments_df.to_excel(writer, sheet_name="Payments", index=False)
            trainers_df.to_excel(writer, sheet_name="Trainers", index=False)


        self.stdout.write(self.style.SUCCESS("Backup Created Successfully"))