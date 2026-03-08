import pandas as pd
from django.http import HttpResponse
from gym.models import Member, Subscription, MembershipPlan, Trainer
from django.utils import timezone
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


def export_gym_data(gym):

    # ---------------- MEMBERS ----------------
    members = Member.objects.filter(gym=gym)

    members_data = [
        {
            "Member Name": m.name,
            "Phone": m.full_phone(),
            "Gender": m.gender,
            "Age": m.age,
            "Join Date": m.join_date,
        }
        for m in members
    ]

    # ---------------- SUBSCRIPTIONS ----------------
    subscriptions = Subscription.objects.filter(gym=gym).select_related("member", "plan")

    subs_data = [
        {
            "Member Code": s.member_code,
            "Member": s.member.name,
            "Plan": s.plan.name,
            "Start Date": s.start_date,
            "Expiry Date": s.expiry_date,
            "Extra Months": s.extra_months,
            "Discount %": s.discount_percent,
            "PT Fee": s.personal_training_fee,
            "Final Amount": s.final_amount,
            "Amount Paid": s.amount_paid,
            "Payment Mode": s.payment_mode,
            "Paid On": s.paid_on,
        }
        for s in subscriptions
    ]

    # ---------------- PLANS ----------------
    plans = MembershipPlan.objects.filter(gym=gym)

    plans_data = [
        {
            "Plan Name": p.name,
            "Price": p.price,
            "Duration (Months)": p.duration_months,
        }
        for p in plans
    ]

    # ---------------- TRAINERS ----------------
    trainers = Trainer.objects.filter(gym=gym)

    trainers_data = [
        {
            "Trainer Code": t.trainer_code,
            "Name": t.name,
            "Phone": t.phone,
            "Gender": t.gender,
            "Experience Years": t.experience_years,
            "Salary": t.salary,
            "Join Date": t.join_date,
            "Shift Start": t.shift_start,
            "Shift End": t.shift_end,
        }
        for t in trainers
    ]

    # ---------------- DATAFRAMES ----------------
    members_df = pd.DataFrame(members_data) if members_data else pd.DataFrame(columns=[
        "Member Name", "Phone", "Gender", "Age", "Join Date"
    ])

    subs_df = pd.DataFrame(subs_data) if subs_data else pd.DataFrame(columns=[
        "Member Code", "Member", "Plan", "Start Date", "Expiry Date",
        "Extra Months", "Discount %", "PT Fee", "Final Amount",
        "Amount Paid", "Payment Mode", "Paid On"
    ])

    plans_df = pd.DataFrame(plans_data) if plans_data else pd.DataFrame(columns=[
        "Plan Name", "Price", "Duration (Months)"
    ])

    trainers_df = pd.DataFrame(trainers_data) if trainers_data else pd.DataFrame(columns=[
        "Trainer Code", "Name", "Phone", "Gender", "Experience Years",
        "Salary", "Join Date", "Shift Start", "Shift End"
    ])

    # ---------------- CREATE EXCEL RESPONSE ----------------
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    now = timezone.localtime()
    timestamp = now.strftime("%d-%m-%Y_%I-%M-%p")

    gym_name_clean = gym.name.replace(" ", "_")
    filename = f"{gym_name_clean}_Report_{timestamp}.xlsx"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    with pd.ExcelWriter(response, engine="openpyxl") as writer:

        members_df.to_excel(writer, sheet_name="Members", index=False)
        subs_df.to_excel(writer, sheet_name="Subscriptions", index=False)
        plans_df.to_excel(writer, sheet_name="Plans", index=False)
        trainers_df.to_excel(writer, sheet_name="Trainer Management", index=False)

        # ---------------- STYLING ----------------
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            # Header style
            for cell in worksheet[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")

            # Auto column width
            for column_cells in worksheet.columns:
                max_length = 0
                column = column_cells[0].column
                column_letter = get_column_letter(column)

                for cell in column_cells:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass

                worksheet.column_dimensions[column_letter].width = max_length + 4

    return response