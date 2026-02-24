from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "document_name",
            "doc_type",
            "division",
            "status",
            "description",
            "date_received_by_peo",
            "date_released_to_admin",
            "date_received_from_admin",
            "date_released_to_accounting",
            "billing_type",
            "percentage",
            "contract_amount",
            "revised_contract_amount",
            "period_covered",
            "date_started",
            "completion_date",
        ]
        widgets = {
            "document_name": forms.TextInput(attrs={"placeholder": "e.g., Site Instruction No. 03"}),
            "doc_type": forms.Select(),
            "division": forms.Select(),
            "status": forms.Select(),
            "description": forms.Textarea(attrs={"rows": 2, "placeholder": "Optional description"}),
            "date_received_by_peo": forms.DateInput(attrs={"type": "date"}),
            "date_released_to_admin": forms.DateInput(attrs={"type": "date"}),
            "date_received_from_admin": forms.DateInput(attrs={"type": "date"}),
            "date_released_to_accounting": forms.DateInput(attrs={"type": "date"}),
            "billing_type": forms.TextInput(attrs={"placeholder": "e.g., Progress Billing #2"}),
            "percentage": forms.NumberInput(attrs={"placeholder": "e.g., 30%", "step": "0.01"}),
            "contract_amount": forms.NumberInput(attrs={"placeholder": "e.g., 50,000.00", "step": "0.01"}),
            "revised_contract_amount": forms.NumberInput(attrs={"placeholder": "e.g., 55,200.00", "step": "0.01"}),
            "period_covered": forms.TextInput(attrs={"placeholder": "e.g., Jan-Mar 2026"}),
            "date_started": forms.DateInput(attrs={"type": "date"}),
            "completion_date": forms.DateInput(attrs={"type": "date"}),
        }

