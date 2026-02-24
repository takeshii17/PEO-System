from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def planning_div_dashboard(request):
    return render(request, 'Planning Division/planning_Div.html')


@login_required
def admin_div_dashboard(request):
    return render(request, 'Admin/admin_div.html')

<<<<<<< HEAD
@login_required
def maintinance_div_dashboard(request):
    return render(request, "Maintinance Division/maintinance_Div.html")
=======

@login_required
def construction_div_dashboard(request):
    return render(request, 'Construction Division/construction_div.html')


@login_required
def quality_div_dashboard(request):
    return render(request, 'Quality Division/quality_div.html')
>>>>>>> 25fb02a0b84d8178b4ea838e419c3e091df30a2f
