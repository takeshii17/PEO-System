from django.shortcuts import render
from django.http import HttpResponse

<<<<<<< HEAD
def admin_div_dashboard(request):
    return render(request, "Admin/adminDiv-dashboard.html")
=======
def home(request):
    return HttpResponse ("<h1>Welcome to the PEO System</h1>")
>>>>>>> 7e05f42bab1268a060c41dd3e7e13bd38da4a9b4
