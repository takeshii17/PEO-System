from django.urls import path

from . import views

urlpatterns = [
    path("admin-division/dashboard/", views.admin_div_dashboard, name="admin_div_dashboard"),
    path("Admin/adminDiv.html", views.admin_div_dashboard, name="admin_div_dashboard_legacy"),
]
