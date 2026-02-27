from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Case, DecimalField, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from decimal import Decimal

from .forms import ConstructionStatusReportForm, DocumentForm, PlanningBudgetForm, PlanningProjectForm
from .models import ConstructionStatusReport, Document, DocumentScan, PlanningBudget, PlanningProject


@login_required
def home(request):
    item_type_choices = [
        ("document", "Document"),
        ("task", "Task"),
        ("project", "Project (go to Projects)"),
    ]
    division_choices = Document.DIVISION_CHOICES
    selected_division = Document.DIV_CONSTRUCTION
    selected_item_type = "document"
    title = ""
    description = ""
    show_new_item_modal = False
    new_item_error = ""

    if request.method == "POST" and request.POST.get("action") == "create_home_item":
        selected_item_type = request.POST.get("item_type", "document").strip().lower()
        selected_division = request.POST.get("division", "").strip()
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        show_new_item_modal = True

        valid_item_types = {value for value, _ in item_type_choices}
        valid_divisions = {value for value, _ in division_choices}

        if selected_item_type not in valid_item_types:
            new_item_error = "Invalid item type."
        elif not title:
            new_item_error = "Title is required."
        elif selected_item_type == "document":
            if selected_division not in valid_divisions:
                new_item_error = "Invalid division selected."
            elif not _table_exists(Document):
                new_item_error = "Document table is not ready yet. Run migrations first."
            else:
                Document.objects.create(
                    document_name=title,
                    doc_type=Document.TYPE_OTHER,
                    division=selected_division,
                    status=Document.STATUS_DRAFT,
                    description=description,
                    created_by=request.user,
                )
                return redirect("admin_div_dashboard")
        elif selected_item_type == "task":
            return redirect("maintinance_task_management")
        elif selected_item_type == "project":
            return redirect(f"{reverse('planning_div_dashboard')}?tab=ppa")

        if selected_item_type != "document" and selected_division not in valid_divisions:
            new_item_error = "Invalid division selected."

    total_documents = 0
    completed_documents = 0
    ongoing_documents = 0
    total_cost_value = Decimal("0")
    recent_projects = []

    if _table_exists(Document):
        documents_qs = Document.objects.all()
        total_documents = documents_qs.count()
        completed_documents = documents_qs.filter(
            status__in=[Document.STATUS_APPROVED, Document.STATUS_CLOSED]
        ).count()
        ongoing_documents = documents_qs.exclude(
            status__in=[Document.STATUS_APPROVED, Document.STATUS_CLOSED]
        ).count()
        total_cost_value = documents_qs.aggregate(
            total=Coalesce(
                Sum(
                    Case(
                        When(revised_contract_amount__isnull=False, then=F("revised_contract_amount")),
                        default=Coalesce(
                            F("contract_amount"),
                            Value(Decimal("0.00"), output_field=DecimalField(max_digits=14, decimal_places=2)),
                            output_field=DecimalField(max_digits=14, decimal_places=2),
                        ),
                        output_field=DecimalField(max_digits=14, decimal_places=2),
                    )
                ),
                Value(Decimal("0.00"), output_field=DecimalField(max_digits=14, decimal_places=2)),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )["total"] or Decimal("0")

    if _table_exists(PlanningProject):
        recent_projects = list(PlanningProject.objects.order_by("-id")[:6])

    def _format_currency_short(amount):
        amount = Decimal(amount or 0)
        absolute = abs(amount)
        if absolute >= Decimal("1000000000"):
            return f"PHP {amount / Decimal('1000000000'):.1f}B"
        if absolute >= Decimal("1000000"):
            return f"PHP {amount / Decimal('1000000'):.1f}M"
        return f"PHP {amount:,.0f}"

    context = {
        "item_type_choices": item_type_choices,
        "division_choices": division_choices,
        "new_item_selected_type": selected_item_type,
        "new_item_selected_division": selected_division,
        "new_item_title": title,
        "new_item_description": description,
        "show_new_item_modal": show_new_item_modal,
        "new_item_error": new_item_error,
        "total_documents": total_documents,
        "completed_documents": completed_documents,
        "ongoing_documents": ongoing_documents,
        "total_cost_display": _format_currency_short(total_cost_value),
        "recent_projects": recent_projects,
    }
    return render(request, "home.html", context)


@login_required
@xframe_options_sameorigin
def planning_div_dashboard(request):
    active_tab = request.GET.get("tab", "budget")
    if active_tab not in {"budget", "ppa", "timeline"}:
        active_tab = "budget"

    selected_fund = request.GET.get("fund", "").strip()
    if not _table_exists(PlanningBudget) or not _table_exists(PlanningProject):
        context = _planning_fallback_context(active_tab=active_tab, selected_fund=selected_fund)
        return render(request, "Planning Division/planning_Div.html", context)

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

        if action == "create_budget":
            budget_form = PlanningBudgetForm(request.POST)
            show_budget_modal = True
            editing_budget = None
            if budget_form.is_valid():
                budget_form.save()
                return redirect(f"{request.path}?tab=budget")
        elif action == "update_budget":
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
@xframe_options_sameorigin
def admin_div_dashboard(request):
    active_tab = request.GET.get("tab", "documents")
    if active_tab not in {"documents", "billing"}:
        active_tab = "documents"
    if not _table_exists(Document):
        context = _admin_fallback_context(active_tab=active_tab)
        return render(request, "Admin/admin_div.html", context)

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
                for uploaded_file in request.FILES.getlist("scanned_files"):
                    if uploaded_file:
                        DocumentScan.objects.create(
                            document=document,
                            project=document.project,
                            file=uploaded_file,
                            uploaded_by=request.user,
                        )
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
@xframe_options_sameorigin
def maintinance_div_dashboard(request):
    return _render_maintinance_dashboard(request)


@login_required
@xframe_options_sameorigin
def construction_div_dashboard(request):
    embedded_mode = bool(request.GET.get("embedded") or request.POST.get("embedded"))
    redirect_url = reverse("construction_div_dashboard")
    if embedded_mode:
        redirect_url = f"{redirect_url}?embedded=1"

    if not _table_exists(ConstructionStatusReport):
        context = {
            "reports": [],
            "report_form": ConstructionStatusReportForm(),
            "show_report_modal": False,
            "editing_report": None,
            "db_not_ready": True,
        }
        return render(request, "Construction Division/construction_div.html", context)

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
            return redirect(redirect_url)

        if action in {"create", "update"}:
            instance = None
            update_error = None
            if action == "update":
                report_id = request.POST.get("report_id")
                if report_id:
                    instance = ConstructionStatusReport.objects.filter(id=report_id).first()
                    editing_report = instance
                if instance is None:
                    update_error = "The selected report no longer exists."
            report_form = ConstructionStatusReportForm(request.POST, instance=instance)
            show_report_modal = True
            if update_error:
                report_form.add_error(None, update_error)
            elif report_form.is_valid():
                report_form.save()
                return redirect(redirect_url)
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
@xframe_options_sameorigin
def quality_div_dashboard(request):
    return render(request, "Quality Division/quality_div.html")


@login_required
@xframe_options_sameorigin
def my_assignments(request):
    return render(request, "My Assignments/my_Assigments.html")


@login_required
@xframe_options_sameorigin
def history_page(request):
    return render(request, "History/history.html")


@login_required
@xframe_options_sameorigin
def projects_dashboard(request):
    query = request.GET.get("q", "").strip()
    division_choices = [
        (Document.DIV_ADMIN, "Admin Division"),
        (Document.DIV_PLANNING, "Planning Division"),
        (Document.DIV_CONSTRUCTION, "Construction Division"),
        (Document.DIV_QUALITY, "Quality Division"),
        (Document.DIV_MAINTENANCE, "Maintenance Division"),
    ]
    valid_divisions = {value for value, _ in division_choices}
    selected_division = request.GET.get("division", Document.DIV_ADMIN).strip().lower()
    if selected_division not in valid_divisions:
        selected_division = Document.DIV_ADMIN

    counts_by_division = {value: 0 for value, _ in division_choices}
    selected_projects = []
    project_folders = []

    if _table_exists(Document):
        for div_key, _ in division_choices:
            counts_by_division[div_key] = Document.objects.filter(division=div_key, project__isnull=False).count()

        documents_qs = (
            Document.objects.filter(division=selected_division, project__isnull=False)
            .select_related("project")
            .prefetch_related("scans")
            .order_by("-created_at")
        )
        if query:
            documents_qs = documents_qs.filter(
                Q(document_name__icontains=query)
                | Q(description__icontains=query)
                | Q(project__project_title__icontains=query)
            )

        folders_map = {}
        for doc in documents_qs:
            project = doc.project
            if not project:
                continue
            bucket = folders_map.setdefault(
                project.id,
                {
                    "project_title": project.project_title,
                    "document_count": 0,
                    "files": [],
                },
            )
            bucket["document_count"] += 1
            for scan in doc.scans.all():
                bucket["files"].append(scan)

        for _, bucket in sorted(folders_map.items(), key=lambda item: item[1]["project_title"].lower()):
            selected_projects.append(
                {
                    "title": bucket["project_title"],
                    "meta": f"{bucket['document_count']} document(s) | {len(bucket['files'])} scan(s)",
                }
            )
            project_folders.append(bucket)

    context = {
        "query": query,
        "selected_division": selected_division,
        "selected_division_label": dict(division_choices).get(selected_division, "Division"),
        "counts_by_division": counts_by_division,
        "selected_projects": selected_projects,
        "project_folders": project_folders,
    }
    return render(request, "Projects/projects.html", context)


@login_required
@xframe_options_sameorigin
def maintinance_task_management(request):
    return _render_maintinance_tasks(request)


@login_required
@xframe_options_sameorigin
def maintinance_contractor_management(request):
    return _render_maintinance_contractors(request)


@login_required
@xframe_options_sameorigin
def maintenance_div_dashboard(request):
    return _render_maintinance_dashboard(request)


@login_required
@xframe_options_sameorigin
def maintenance_task_management(request):
    return _render_maintinance_tasks(request)


@login_required
@xframe_options_sameorigin
def maintenance_contractor_management(request):
    return _render_maintinance_contractors(request)


def _render_maintinance_dashboard(request):
    return render(request, "Maintinance Division/maintinance_management.html")


def _render_maintinance_tasks(request):
    return render(request, "Maintinance Division/task_management.html")


def _render_maintinance_contractors(request):
    return render(request, "Maintinance Division/contractor_management.html")


def _table_exists(model):
    table_name = model._meta.db_table
    try:
        return table_name in connection.introspection.table_names()
    except Exception:
        return False


def _planning_fallback_context(active_tab="budget", selected_fund=""):
    return {
        "active_tab": active_tab,
        "selected_fund": selected_fund,
        "budgets": [],
        "budget_form": PlanningBudgetForm(),
        "show_budget_modal": False,
        "editing_budget": None,
        "project_form": PlanningProjectForm(initial={"fund": selected_fund or PlanningBudget.FUND_20_DEV}),
        "show_project_modal": False,
        "ppa_projects": [],
        "ppa_search": "",
        "ppa_status": "",
        "ppa_fund": "",
        "ppa_total": 0,
        "ppa_approved": 0,
        "ppa_for_review": 0,
        "ppa_total_cost": Decimal("0"),
        "project_status_choices": PlanningProject.STATUS_CHOICES,
        "fund_choices": PlanningBudget.FUND_CHOICES,
        "total_budgets": 0,
        "total_allocated": Decimal("0"),
        "total_remaining": Decimal("0"),
        "db_not_ready": True,
    }


def _admin_fallback_context(active_tab="documents"):
    empty_page = Paginator([], 8).get_page(1)
    return {
        "active_tab": active_tab,
        "form": DocumentForm(),
        "show_modal": False,
        "editing_document": None,
        "documents": [],
        "billing_records": [],
        "page_obj": empty_page,
        "search": "",
        "selected_division": "",
        "selected_status": "",
        "division_choices": Document.DIVISION_CHOICES,
        "status_choices": Document.STATUS_CHOICES,
        "total_documents": 0,
        "for_review_count": 0,
        "processing_count": 0,
        "open_issues_count": 0,
        "total_billing_records": 0,
        "billing_for_review_count": 0,
        "billing_processing_count": 0,
        "billing_approved_count": 0,
        "db_not_ready": True,
    }
