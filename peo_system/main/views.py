from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from decimal import Decimal

from .forms import ConstructionStatusReportForm, DocumentForm, PlanningBudgetForm, PlanningProjectForm
from .models import ConstructionStatusReport, Document, PlanningBudget, PlanningProject


@login_required
def home(request):
    return render(request, "home.html")


@login_required
def planning_div_dashboard(request):
    active_tab = request.GET.get("tab", "budget")
    if active_tab not in {"budget", "ppa", "timeline"}:
        active_tab = "budget"

    selected_fund = request.GET.get("fund", "").strip()

    if not PlanningBudget.objects.exists():
        PlanningBudget.objects.create(
            name="20% Development Fund FY 2026",
            fund=PlanningBudget.FUND_20_DEV,
            fiscal_year="FY 2026",
            total_budget=625105288,
            allocated_amount=0,
            status=PlanningBudget.STATUS_APPROVED,
        )
        PlanningBudget.objects.create(
            name="SEF FY 2026",
            fund=PlanningBudget.FUND_SEF,
            fiscal_year="FY 2026",
            total_budget=62994000,
            allocated_amount=0,
            status=PlanningBudget.STATUS_APPROVED,
        )

    budgets = list(PlanningBudget.objects.all())
    projects = PlanningProject.objects.all()
    show_budget_modal = False
    editing_budget = None
    show_project_modal = False
    project_form = PlanningProjectForm(initial={"fund": selected_fund or PlanningBudget.FUND_20_DEV})

    edit_budget_id = request.GET.get("edit_budget")
    if edit_budget_id:
        editing_budget = PlanningBudget.objects.filter(id=edit_budget_id).first()
        if editing_budget:
            show_budget_modal = True

    ppa_search = request.GET.get("q", "").strip()
    ppa_status = request.GET.get("status", "").strip()
    ppa_fund = request.GET.get("fund_filter", selected_fund).strip()

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        if action == "delete_budget":
            delete_id = request.POST.get("delete_id")
            if delete_id:
                PlanningBudget.objects.filter(id=delete_id).delete()
            return redirect(f"{request.path}?tab=budget")

        if action == "update_budget":
            budget_id = request.POST.get("budget_id")
            editing_budget = PlanningBudget.objects.filter(id=budget_id).first()
            budget_form = PlanningBudgetForm(request.POST, instance=editing_budget)
            show_budget_modal = True
            if budget_form.is_valid():
                budget_form.save()
                return redirect(f"{request.path}?tab=budget")
        elif action == "create_project":
            project_form = PlanningProjectForm(request.POST)
            show_project_modal = True
            if project_form.is_valid():
                project = project_form.save()
                return redirect(
                    f"{request.path}?tab=ppa&fund={project.fund}"
                )
            budget_form = PlanningBudgetForm(instance=editing_budget) if editing_budget else PlanningBudgetForm()
        elif action == "delete_project":
            project_id = request.POST.get("project_id")
            if project_id:
                PlanningProject.objects.filter(id=project_id).delete()
            return redirect(f"{request.path}?tab=ppa&fund={selected_fund or ''}")
        else:
            budget_form = PlanningBudgetForm(instance=editing_budget) if editing_budget else PlanningBudgetForm()
    else:
        budget_form = PlanningBudgetForm(instance=editing_budget) if editing_budget else PlanningBudgetForm()

    project_totals = {key: Decimal("0") for key, _ in PlanningBudget.FUND_CHOICES}
    for project in projects:
        project_totals[project.fund] = project_totals.get(project.fund, Decimal("0")) + (project.budget_amount or 0)

    for budget in budgets:
        budget.computed_allocated = project_totals.get(budget.fund, Decimal("0"))

    total_allocated = sum((b.allocated_value for b in budgets), Decimal("0"))
    total_remaining = sum((b.remaining_amount for b in budgets), Decimal("0"))

    ppa_projects = projects
    if ppa_search:
        ppa_projects = ppa_projects.filter(project_title__icontains=ppa_search)
    if ppa_status:
        ppa_projects = ppa_projects.filter(status=ppa_status)
    if ppa_fund:
        ppa_projects = ppa_projects.filter(fund=ppa_fund)

    ppa_total = projects.count()
    ppa_approved = projects.filter(status=PlanningProject.STATUS_APPROVED).count()
    ppa_for_review = projects.filter(status=PlanningProject.STATUS_FOR_REVIEW).count()
    ppa_total_cost = sum((p.budget_amount for p in projects), Decimal("0"))

    context = {
        "active_tab": active_tab,
        "selected_fund": selected_fund,
        "budgets": budgets,
        "budget_form": budget_form,
        "show_budget_modal": show_budget_modal,
        "editing_budget": editing_budget,
        "project_form": project_form,
        "show_project_modal": show_project_modal,
        "ppa_projects": ppa_projects,
        "ppa_search": ppa_search,
        "ppa_status": ppa_status,
        "ppa_fund": ppa_fund,
        "ppa_total": ppa_total,
        "ppa_approved": ppa_approved,
        "ppa_for_review": ppa_for_review,
        "ppa_total_cost": ppa_total_cost,
        "project_status_choices": PlanningProject.STATUS_CHOICES,
        "fund_choices": PlanningBudget.FUND_CHOICES,
        "total_budgets": len(budgets),
        "total_allocated": total_allocated,
        "total_remaining": total_remaining,
    }
    return render(request, "Planning Division/planning_Div.html", context)


@login_required
def admin_div_dashboard(request):
    active_tab = request.GET.get("tab", "documents")
    if active_tab not in {"documents", "billing"}:
        active_tab = "documents"

    form = DocumentForm()
    show_modal = False
    editing_document = None

    edit_document_id = request.GET.get("edit_document")
    if active_tab == "documents" and edit_document_id:
        editing_document = Document.objects.filter(id=edit_document_id).first()
        if editing_document:
            form = DocumentForm(instance=editing_document)
            show_modal = True

    if request.method == "POST" and active_tab == "documents":
        action = request.POST.get("action", "create").strip()

        if action == "delete_document":
            delete_id = request.POST.get("delete_id")
            if delete_id:
                Document.objects.filter(id=delete_id).delete()
            return redirect("admin_div_dashboard")

        if action in {"create", "update"}:
            instance = None
            if action == "update":
                document_id = request.POST.get("document_id")
                if document_id:
                    instance = Document.objects.filter(id=document_id).first()
                    editing_document = instance

            form = DocumentForm(request.POST, instance=instance)
            show_modal = True
            if form.is_valid():
                document = form.save(commit=False)
                if instance is None:
                    document.created_by = request.user
                document.save()
                return redirect("admin_div_dashboard")

    search = request.GET.get("q", "").strip()
    division = request.GET.get("division", "").strip()
    status = request.GET.get("status", "").strip()

    documents_qs = Document.objects.all()

    if search:
        search_l = search.lower()
        matching_types = [
            value
            for value, label in Document.TYPE_CHOICES
            if search_l in label.lower() or search_l in value.replace("_", " ").lower()
        ]
        matching_divisions = [
            value
            for value, label in Document.DIVISION_CHOICES
            if search_l in label.lower() or search_l in value.replace("_", " ").lower()
        ]
        matching_statuses = [
            value
            for value, label in Document.STATUS_CHOICES
            if search_l in label.lower() or search_l in value.replace("_", " ").lower()
        ]
        documents_qs = documents_qs.filter(
            Q(document_name__icontains=search)
            | Q(billing_type__icontains=search)
            | Q(description__icontains=search)
            | Q(doc_type__in=matching_types)
            | Q(division__in=matching_divisions)
            | Q(status__in=matching_statuses)
        )

    documents_filtered = documents_qs
    if division:
        documents_filtered = documents_filtered.filter(division=division)
    if status:
        documents_filtered = documents_filtered.filter(status=status)

    billing_qs = documents_qs.filter(
        Q(billing_type__isnull=False) & ~Q(billing_type="")
        | Q(doc_type=Document.TYPE_BILLING_PACKET)
    )
    if status:
        billing_qs = billing_qs.filter(status=status)

    if active_tab == "billing":
        paginator = Paginator(billing_qs, 8)
    else:
        paginator = Paginator(documents_filtered, 8)
    page_obj = paginator.get_page(request.GET.get("page"))

    billing_base = Document.objects.filter(
        Q(billing_type__isnull=False) & ~Q(billing_type="")
        | Q(doc_type=Document.TYPE_BILLING_PACKET)
    )

    context = {
        "active_tab": active_tab,
        "form": form,
        "show_modal": show_modal,
        "editing_document": editing_document,
        "documents": page_obj.object_list if active_tab == "documents" else documents_filtered[:0],
        "billing_records": page_obj.object_list if active_tab == "billing" else billing_qs[:0],
        "page_obj": page_obj,
        "search": search,
        "selected_division": division,
        "selected_status": status,
        "division_choices": Document.DIVISION_CHOICES,
        "status_choices": Document.STATUS_CHOICES,
        "total_documents": Document.objects.count(),
        "for_review_count": Document.objects.filter(status=Document.STATUS_FOR_REVIEW).count(),
        "processing_count": Document.objects.filter(status=Document.STATUS_PROCESSING).count(),
        "open_issues_count": Document.objects.filter(status=Document.STATUS_OPEN).count(),
        "total_billing_records": billing_base.count(),
        "billing_for_review_count": billing_base.filter(status=Document.STATUS_FOR_REVIEW).count(),
        "billing_processing_count": billing_base.filter(status=Document.STATUS_PROCESSING).count(),
        "billing_approved_count": billing_base.filter(status=Document.STATUS_APPROVED).count(),
    }
    return render(request, "Admin/admin_div.html", context)


@login_required
def maintinance_div_dashboard(request):
    return render(request, "Maintinance Division/maintinance_Div.html")


@login_required
def construction_div_dashboard(request):
    reports = ConstructionStatusReport.objects.all()
    show_report_modal = False
    editing_report = None

    edit_id = request.GET.get("edit")
    if edit_id:
        editing_report = ConstructionStatusReport.objects.filter(id=edit_id).first()
        if editing_report:
            show_report_modal = True

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        if action == "delete":
            delete_id = request.POST.get("delete_id")
            if delete_id:
                ConstructionStatusReport.objects.filter(id=delete_id).delete()
            return redirect("construction_div_dashboard")

        if action in {"create", "update"}:
            instance = None
            if action == "update":
                report_id = request.POST.get("report_id")
                if report_id:
                    instance = ConstructionStatusReport.objects.filter(id=report_id).first()
                    editing_report = instance
            report_form = ConstructionStatusReportForm(request.POST, instance=instance)
            show_report_modal = True
            if report_form.is_valid():
                report_form.save()
                return redirect("construction_div_dashboard")
        else:
            report_form = ConstructionStatusReportForm()
    else:
        report_form = (
            ConstructionStatusReportForm(instance=editing_report)
            if editing_report
            else ConstructionStatusReportForm()
        )

    context = {
        "reports": reports,
        "report_form": report_form,
        "show_report_modal": show_report_modal,
        "editing_report": editing_report,
    }
    return render(request, "Construction Division/construction_div.html", context)


@login_required
def quality_div_dashboard(request):
    return render(request, "Quality Division/quality_div.html")
