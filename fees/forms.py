"""Fees forms"""
from django import forms
from django.utils import timezone
from datetime import time, datetime
import pytz
from .models import FeeStructure, FeeInvoice, FeePayment, PaymentConfig, Expense, ExpenseCategory
from academics.models import ClassLevel, AcademicYear
from results.models import Term


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['name', 'class_level', 'academic_year', 'term', 'amount', 'currency', 'is_mandatory', 'due_date', 'description']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, school=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['class_level'].queryset = ClassLevel.objects.filter(school=school)
            self.fields['academic_year'].queryset = AcademicYear.objects.filter(school=school)
            self.fields['term'].queryset = Term.objects.filter(academic_year__school=school)
            self.fields['class_level'].required = False
            self.fields['term'].required = False


class FeeInvoiceForm(forms.ModelForm):
    class Meta:
        model = FeeInvoice
        fields = ['student', 'fee_structure', 'amount', 'currency', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, school=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            from academics.models import Student
            self.fields['student'].queryset = Student.objects.filter(school=school, is_active=True).select_related('user')
            self.fields['fee_structure'].queryset = FeeStructure.objects.filter(school=school)
            self.fields['fee_structure'].required = False


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['amount', 'currency', 'method', 'reference', 'payment_date', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def clean_payment_date(self):
        date_obj = self.cleaned_data.get('payment_date')
        if date_obj:
            tz = pytz.timezone('Africa/Harare')
            dt = tz.localize(datetime.combine(date_obj, time(12, 0)))
            self.instance.payment_date = dt
        else:
            self.instance.payment_date = timezone.now()
        return self.cleaned_data.get('payment_date')


class PaymentConfigForm(forms.ModelForm):
    class Meta:
        model = PaymentConfig
        fields = [
            'accept_cash', 'accept_paynow', 'paynow_integration_id', 'paynow_integration_key',
            'paynow_result_url', 'paynow_return_url',
            'accept_ecocash', 'ecocash_merchant_code',
            'accept_bank_transfer', 'bank_name', 'bank_account_number', 'bank_branch',
        ]


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'title', 'amount', 'currency', 'date', 'reference', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, school=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['category'].queryset = ExpenseCategory.objects.filter(school=school)
