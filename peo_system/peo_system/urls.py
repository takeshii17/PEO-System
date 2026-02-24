
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from main.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', home, name='home'),
=======
    path('', include('main.urls')),

    path ('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path ('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path ('',home, name='home'),
>>>>>>> d09195ab9d34895369dfe9ffb3602105326bbe5f
]
