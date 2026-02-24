from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, 'home.html')

<<<<<<< HEAD
=======
@login_required
def planning_div_dashboard(request):
    return render(request, "Planning Division/planning_Div.html")

def admin_div_dashboard(request):
    return render(request, "Admin/adminDiv-dashboard.html")
>>>>>>> f058333f2f33ddb5dc37a62b7d43a50b344e6284

@login_required
def admin_div_dashboard(request):
    return render(request, 'Admin/admin_div.html')
