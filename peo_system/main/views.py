from django.shortcuts import render

def admin_div_dashboard(request):
    return render(request, "Admin/adminDiv-dashboard.html")
