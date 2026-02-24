from django.urls import path

from . import views

urlpatterns = [
<<<<<<< HEAD
    path("", views.home, name="home"),
    path("templates/home.html", views.home, name="home_template_alias"),
    path("planning-division/dashboard/", views.planning_div_dashboard, name="planning_div_dashboard"),
    path("admin-division/dashboard/", views.admin_div_dashboard, name="admin_div_dashboard"),
    path("maintinance-division/dashboard/", views.maintinance_div_dashboard, name="maintinance_div_dashboard"),
    path("Admin/adminDiv.html", views.admin_div_dashboard, name="admin_div_dashboard_legacy"),
=======
    path('', views.home, name='home'),
    path('templates/home.html', views.home, name='home_template_alias'),
    path('planning-division/dashboard/', views.planning_div_dashboard, name='planning_div_dashboard'),
    path('admin-division/dashboard/', views.admin_div_dashboard, name='admin_div_dashboard'),
    path('construction-division/dashboard/', views.construction_div_dashboard, name='construction_div_dashboard'),
    path('quality-division/dashboard/', views.quality_div_dashboard, name='quality_div_dashboard'),
    path('Admin/adminDiv.html', views.admin_div_dashboard, name='admin_div_dashboard_legacy'),
>>>>>>> 25fb02a0b84d8178b4ea838e419c3e091df30a2f
]
