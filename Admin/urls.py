from django.urls import path
from . import views

urlpatterns = [
    path('check-auth/',views.CheckAuth.as_view()),
    path('login/',views.AdminLogin.as_view()),
]