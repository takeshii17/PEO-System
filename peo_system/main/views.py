from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import DocumentForm
from .models import Document


@login_required
def home(request):
    return render(request, "home.html")


@login_required
def planning_div_dashboard(request):
    return render(request, "Planning Division/planning_Div.html")


@login_required
def admin_div_dashboard(request):
    form = DocumentForm()
    show_modal = False

    if request.method == "POST":
        form = DocumentForm(request.POST)
        show_modal = True
        if form.is_valid():
            document = form.save(commit=False)
            document.created_by = request.user
            document.save()
            return redirect("admin_div_dashboard")

    search = request.GET.get("q", "").strip()
    division = request.GET.get("division", "").strip()
    status = request.GET.get("status", "").strip()

    documents = Document.objects.all()

    if search:
        documents = documents.filter(
            Q(document_name__icontains=search)
            | Q(billing_type__icontains=search)
            | Q(description__icontains=search)
        )
    if division:
        documents = documents.filter(division=division)
    if status:
        documents = documents.filter(status=status)

    paginator = Paginator(documents, 8)
    page_obj = paginator.get_page(request.GET.get("page"))

    total_documents = Document.objects.count()
    for_review_count = Document.objects.filter(status=Document.STATUS_FOR_REVIEW).count()
    processing_count = Document.objects.filter(status=Document.STATUS_PROCESSING).count()
    open_issues_count = Document.objects.filter(status=Document.STATUS_OPEN).count()

    context = {
        "form": form,
        "show_modal": show_modal,
        "documents": page_obj.object_list,
        "page_obj": page_obj,
        "search": search,
        "selected_division": division,
        "selected_status": status,
        "division_choices": Document.DIVISION_CHOICES,
        "status_choices": Document.STATUS_CHOICES,
        "total_documents": total_documents,
        "for_review_count": for_review_count,
        "processing_count": processing_count,
        "open_issues_count": open_issues_count,
    }
    return render(request, "Admin/admin_div.html", context)


@login_required
def construction_div_dashboard(request):
    return render(request, "Construction Division/construction_div.html")


@login_required
def quality_div_dashboard(request):
    return render(request, "Quality Division/quality_div.html")


@login_required
def maintinance_div_dashboard(request):
    return render(request, "Maintinance Division/maintinance_Div.html")
