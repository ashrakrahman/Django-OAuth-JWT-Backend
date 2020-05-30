from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^home/', views.home, name='home'),
    url(r'^oauth/register/', views.register, name='register'),
    url(r'^oauth/login/', views.login, name='login'),
    url(r'^oauth/refresh/', views.refresh, name='refresh'),
    url(r'^user/info/', views.get_user_info, name='user_info'),
]
