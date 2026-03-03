import pandas as pd
from django.http import HttpResponse
from gym.models import Member, Subscription, MembershipPlan
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
            "Join Date": m.join_date,
        }
        for m in members
    ]

    # ---------------- SUBSCRIPTIONS ----------------
    subscriptions = Subscription.objects.filter(gym=gym).select_related("member", "plan")

    subs_data = [
        {
            "Member": s.member.name,
            "Plan": s.plan.name,
            "Start Date": s.start_date,
            "Expiry Date": s.expiry_date,
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

    # Convert to DataFrames
    members_df = pd.DataFrame(members_data)
    subs_df = pd.DataFrame(subs_data)
    plans_df = pd.DataFrame(plans_data)

    # Create Excel response
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

        workbook = writer.book

        # Apply styling + auto width
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            # ✅ Bold + Center Header
            for cell in worksheet[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")

            # ✅ Auto Column Width
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

                adjusted_width = max_length + 4
                worksheet.column_dimensions[column_letter].width = adjusted_width

    return response