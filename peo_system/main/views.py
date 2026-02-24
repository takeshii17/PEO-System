from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def planning_div_dashboard(request):
    return render(request, "Planning Division/planning_Div.html")

@login_required
def admin_div_dashboard(request):
    return render(request, 'Admin/admin_div.html')

@login_required
def maintinance_div_dashboard(request):
    return render(request, "Maintinance Division/maintinance_Div.html")
