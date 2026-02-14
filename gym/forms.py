from django import forms
from .models import Member, MembershipPlan, Subscription


# ======================================================
# 👤 MEMBER FORM
# ======================================================

from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter member name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.gym = kwargs.pop('gym', None)
        super().__init__(*args, **kwargs)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if Member.objects.filter(
            gym=self.gym,
            phone=phone
        ).exists():
            raise forms.ValidationError(
                "This phone number already exists in your gym."
            )

        return phone


# ======================================================
# 💳 PLAN FORM
# ======================================================

class PlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ['name', 'price', 'duration_days']

    def __init__(self, *args, **kwargs):
        self.gym = kwargs.pop('gym', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')

        # Prevent duplicate plan name inside same gym
        if MembershipPlan.objects.filter(gym=self.gym, name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "A plan with this name already exists."
            )

        return name


# ======================================================
# 📋 SUBSCRIPTION FORM
# ======================================================

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['member', 'plan', 'expiry_date']

    def __init__(self, *args, **kwargs):
        self.gym = kwargs.pop('gym', None)
        super().__init__(*args, **kwargs)

        # 🔥 Filter only this gym's members & plans
        if self.gym:
            self.fields['member'].queryset = self.gym.member_set.all()
            self.fields['plan'].queryset = self.gym.membershipplan_set.all()

    def clean_member(self):
        member = self.cleaned_data.get('member')

        # Only one subscription per member
        if Subscription.objects.filter(member=member).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "This member already has a subscription."
            )

        return member
