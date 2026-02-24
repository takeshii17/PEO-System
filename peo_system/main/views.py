from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    return render(request, "home.html")


@login_required
def planning_div_dashboard(request):
    return render(request, "Planning Division/planning_Div.html")


@login_required
def admin_div_dashboard(request):
    return render(request, "Admin/admin_div.html")


@login_required
def maintinance_div_dashboard(request):
    return render(request, "Maintinance Division/maintinance_Div.html")


@login_required
def construction_div_dashboard(request):
    return render(request, "Construction Division/construction_div.html")


@login_required
def quality_div_dashboard(request):
    return render(request, "Quality Division/quality_div.html")
