from django import forms

from .models import ConstructionStatusReport, Document, PlanningBudget, PlanningProject


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "document_name",
            "doc_type",
            "division",
            "project",
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
            "project": forms.Select(),
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


class PlanningBudgetForm(forms.ModelForm):
    class Meta:
        model = PlanningBudget
        fields = ["name", "fund", "fiscal_year", "total_budget", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g., 20% Development Fund FY 2026"}),
            "fund": forms.Select(),
            "fiscal_year": forms.TextInput(attrs={"placeholder": "e.g., FY 2026"}),
            "total_budget": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "status": forms.Select(),
        }

    def clean_total_budget(self):
        total_budget = self.cleaned_data.get("total_budget")
        if total_budget is not None and total_budget < 0:
            raise forms.ValidationError("Total budget cannot be negative.")
        return total_budget


class PlanningProjectForm(forms.ModelForm):
    class Meta:
        model = PlanningProject
        fields = ["project_title", "fund", "budget_amount", "status"]
        widgets = {
            "project_title": forms.TextInput(attrs={"placeholder": "e.g., Road Improvement Program"}),
            "fund": forms.Select(),
            "budget_amount": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "status": forms.Select(),
        }

    def clean_budget_amount(self):
        budget_amount = self.cleaned_data.get("budget_amount")
        if budget_amount is not None and budget_amount < 0:
            raise forms.ValidationError("Budget amount cannot be negative.")
        return budget_amount


class ConstructionStatusReportForm(forms.ModelForm):
    class Meta:
        model = ConstructionStatusReport
        fields = [
            "project_name",
            "location",
            "mun",
            "contractor",
            "contract_cost",
            "ntp_date",
            "cd",
            "original_expiry_date",
            "additional_cd",
            "revised_expiry_date",
            "date_completed",
            "revised_contract_cost",
            "status_previous",
            "status_current",
            "percent_time_elapsed",
            "slippage_percent",
            "remarks",
        ]
        widgets = {
            "project_name": forms.TextInput(attrs={"placeholder": "e.g., Bridge Rehabilitation Project"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g., Barangay San Isidro"}),
            "mun": forms.TextInput(attrs={"placeholder": "Municipality"}),
            "contractor": forms.TextInput(attrs={"placeholder": "Contractor name"}),
            "contract_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "ntp_date": forms.DateInput(attrs={"type": "date"}),
            "cd": forms.NumberInput(attrs={"min": "0"}),
            "original_expiry_date": forms.DateInput(attrs={"type": "date"}),
            "additional_cd": forms.NumberInput(attrs={"min": "0"}),
            "revised_expiry_date": forms.TextInput(attrs={"placeholder": "e.g., June 15, 2026"}),
            "date_completed": forms.DateInput(attrs={"type": "date"}),
            "revised_contract_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "status_previous": forms.TextInput(attrs={"placeholder": "e.g., 65%"}),
            "status_current": forms.TextInput(attrs={"placeholder": "e.g., 72%"}),
            "percent_time_elapsed": forms.NumberInput(attrs={"step": "0.01"}),
            "slippage_percent": forms.NumberInput(attrs={"step": "0.01"}),
            "remarks": forms.Textarea(attrs={"rows": 3, "placeholder": "Additional details"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cd = cleaned_data.get("cd")
        additional_cd = cleaned_data.get("additional_cd")
        if cd is not None and cd < 0:
            self.add_error("cd", "C.D cannot be negative.")
        if additional_cd is not None and additional_cd < 0:
            self.add_error("additional_cd", "Additional C.D cannot be negative.")
        return cleaned_data
