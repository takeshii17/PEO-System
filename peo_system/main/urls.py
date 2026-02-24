from django.urls import path

from . import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),
    path("dashboard/", views.home, name="dashboard"),

    # Admin Division
    path("admin-division/dashboard/", views.admin_div_dashboard, name="admin_div_dashboard"),
    path("admin-division/", views.admin_div_dashboard, name="admin_division"),

    # Planning Division
    path("planning-division/dashboard/", views.planning_div_dashboard, name="planning_div_dashboard"),
    path("planning-division/", views.planning_div_dashboard, name="planning_division"),

    # Construction Division
    path("construction-division/dashboard/", views.construction_div_dashboard, name="construction_div_dashboard"),
    path("construction-division/", views.construction_div_dashboard, name="construction_division"),

    # Quality Division
    path("quality-division/dashboard/", views.quality_div_dashboard, name="quality_div_dashboard"),
    path("quality-division/", views.quality_div_dashboard, name="quality_division"),

    # Maintenance Division (legacy typo + canonical spelling)
    path("maintinance-division/dashboard/", views.maintinance_div_dashboard, name="maintinance_div_dashboard"),
    path("maintinance-division/", views.maintinance_div_dashboard, name="maintinance_division"),
    path("maintinance-division/management/", views.maintinance_div_dashboard, name="maintinance_management"),
    path("maintenance-division/dashboard/", views.maintenance_div_dashboard, name="maintenance_div_dashboard"),
    path("maintenance-division/", views.maintenance_div_dashboard, name="maintenance_division"),
    path("maintenance-division/management/", views.maintenance_div_dashboard, name="maintenance_management"),

    # My Assignments
    path("my-assignments/", views.my_assignments, name="my_assignments"),

    # Tasks
    path("maintinance-division/tasks/", views.maintinance_task_management, name="maintinance_task_management"),
    path("maintenance-division/tasks/", views.maintenance_task_management, name="maintenance_task_management"),
    path("tasks/", views.maintinance_task_management, name="tasks"),

    # Contractors
    path("maintinance-division/contractors/", views.maintinance_contractor_management, name="maintinance_contractor_management"),
    path("maintenance-division/contractors/", views.maintenance_contractor_management, name="maintenance_contractor_management"),
    path("contractors/", views.maintinance_contractor_management, name="contractors"),

    # Legacy direct aliases
    path("templates/home.html", views.home, name="home_template_alias"),
    path("templates/my_Assigments.html", views.my_assignments, name="my_assignments_template_alias"),
    path("Admin/adminDiv.html", views.admin_div_dashboard, name="admin_div_dashboard_legacy"),
]
