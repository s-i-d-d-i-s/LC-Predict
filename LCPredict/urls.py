"""LCPredict URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views as main_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_view.homepage, name='home'),
    path('admin_panel', main_view.allcontests, name='contests'),
    path('predictions', main_view.predictions, name='predictions'),
    path('api/predict/<apikey>/<pk>', main_view.predict_contest_api, name='predict_contest_api'),
	path('api/statusupdate/<apikey>/<operation>', main_view.status_updates_api, name='status_updates_api'),
    path('api/status/<apikey>/<pk>', main_view.get_contest_status, name='predict_contest_api'),
    path('predict/<pk>/<username>', main_view.predict_user, name='predict_user'),
    path('cache/<pk>', main_view.cache_contest, name='cache_contest'),
    path('dashboard',main_view.dashboard,name='dashboard'),
	path('foresight',main_view.foresight,name='foresight'),
	path('api/foresight',main_view.foresight_api,name='foresight_api'),
	path('register',main_view.register,name='register'),
	path('verify',main_view.verify_account,name='verify'),
	path('api/verify',main_view.verify_account_api,name='verify_api'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='main/logout.html'), name='logout'),
]
