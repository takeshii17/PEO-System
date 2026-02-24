from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("templates/home.html", views.home, name="home_template_alias"),
    path("planning-division/dashboard/", views.planning_div_dashboard, name="planning_div_dashboard"),
    path("admin-division/dashboard/", views.admin_div_dashboard, name="admin_div_dashboard"),
    path("construction-division/dashboard/", views.construction_div_dashboard, name="construction_div_dashboard"),
    path("quality-division/dashboard/", views.quality_div_dashboard, name="quality_div_dashboard"),
    path("maintinance-division/dashboard/", views.maintinance_div_dashboard, name="maintinance_div_dashboard"),
    path("maintenance-division/dashboard/", views.maintenance_div_dashboard, name="maintenance_div_dashboard"),
    path("maintenance-division/management/", views.maintenance_div_dashboard, name="maintenance_management"),
    path("construction-division/dashboard/", views.construction_div_dashboard, name="construction_div_dashboard"),
    path("quality-division/dashboard/", views.quality_div_dashboard, name="quality_div_dashboard"),
    path("my-assignments/", views.my_assignments, name="my_assignments"),
    path("maintinance-division/tasks/", views.maintinance_task_management, name="maintinance_task_management"),
    path("maintenance-division/tasks/", views.maintenance_task_management, name="maintenance_task_management"),
    path("maintinance-division/contractors/", views.maintinance_contractor_management, name="maintinance_contractor_management"),
    path("maintenance-division/contractors/", views.maintenance_contractor_management, name="maintenance_contractor_management"),
    path("Admin/adminDiv.html", views.admin_div_dashboard, name="admin_div_dashboard_legacy"),
<<<<<<< HEAD
]
=======
]

>>>>>>> ec65c4109cb74a406ca21594a5c16fec1969a552
