from django import forms
from .models import Member, MembershipPlan, Subscription
from django.utils import timezone

# ======================================================
# 👤 MEMBER FORM
# ======================================================

COUNTRY_CHOICES = [
    ("+91", "🇮🇳 India (+91)"),
    ("+971", "🇦🇪 UAE (+971)"),
    ("+1", "🇺🇸 USA (+1)"),
    ("+44", "🇬🇧 UK (+44)"),
    ("+60", "🇲🇾 Malaysia (+60)"),
]


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'country_code', 'phone', 'gender', 'age', 'join_date']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),

            'country_code': forms.Select(
                choices=COUNTRY_CHOICES,
                attrs={'class': 'form-control'}
            ),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter 10 digit number'
            }),

            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),

            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter age'
            }),

            'join_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.gym = kwargs.pop('gym', None)
        super().__init__(*args, **kwargs)

        self.fields['country_code'].initial = "+91"

        # Auto join date
        if not self.instance.pk:
            self.fields['join_date'].initial = timezone.now().date()

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone or not phone.isdigit():
            raise forms.ValidationError("Phone must contain only digits.")

        if len(phone) != 10:
            raise forms.ValidationError("Enter valid 10 digit number.")

        if phone[0] not in ['6','7','8','9']:
            raise forms.ValidationError("Invalid Indian mobile number.")

        existing = Member.objects.filter(gym=self.gym, phone=phone)

        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise forms.ValidationError("This number already exists.")

        return phone

# ======================================================
# 💳 PLAN FORM
# ======================================================

class PlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ['name', 'price', 'duration_months']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: 1 Month / 3 Month / Yearly'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter plan price'
            }),
            'duration_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of months (1, 3, 6, 12...)'
            }),
        }


# ======================================================
# 📋 SUBSCRIPTION FORM
# ======================================================

class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = [
            'member',
            'plan',
            'start_date',
            'extra_months',
            'discount_percent',
            'personal_training_fee',
            'payment_mode',   # ✅ ADD THIS

        ]

        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'plan': forms.Select(attrs={'class': 'form-control'}),

            'extra_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),

            'discount_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 0.01
            }),

            'personal_training_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),

            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'payment_mode': forms.Select(attrs={
                'class': 'form-control'
}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # default start_date to today for new subscriptions
        if 'start_date' in self.fields and not self.initial.get('start_date'):
            self.fields['start_date'].initial = timezone.now().date()

    def clean_extra_months(self):
        return self.cleaned_data.get('extra_months') or 0

    def clean_discount_percent(self):
        return self.cleaned_data.get('discount_percent') or 0

    def clean_personal_training_fee(self):
        return self.cleaned_data.get('personal_training_fee') or 0
