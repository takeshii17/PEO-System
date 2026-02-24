from django.shortcuts import render
from django.contrib.auth.decorators import login_required



@login_required
def home(request):
    return render(request, 'home.html')

def admin_div_dashboard(request):
    return render(request, "Admin/adminDiv-dashboard.html")

