from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("templates/home.html", views.home, name="home_template_alias"),
    path("admin-division/dashboard/", views.admin_div_dashboard, name="admin_div_dashboard"),
    path("Admin/adminDiv.html", views.admin_div_dashboard, name="admin_div_dashboard_legacy"),
]
