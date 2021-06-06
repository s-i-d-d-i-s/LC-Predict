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
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_view.homepage, name='home'),
    path('contests', main_view.allcontests, name='contests'),
    path('status', main_view.status, name='status'),
    path('api/predict/<apikey>/<pk>', main_view.predict_contest_api, name='predict_contest_api'),
    path('api/status/<apikey>/<pk>', main_view.get_contest_status, name='predict_contest_api'),
    path('predict/<pk>/<username>', main_view.predict_user, name='predict_user'),
    path('cache/<pk>', main_view.cache_contest, name='cache_contest'),
]
