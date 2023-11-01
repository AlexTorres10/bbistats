
from django.contrib import admin
from django.urls import path, re_path
from app_bbistats import views  # Importe os views do app

urlpatterns = [
    # rota, view responsável, nome de referência
    # bbistats.com
    path('', views.home, name='home'),
    path('ligas/<str:liga>', views.liga, name='ligas'),
    path('times/<str:team_name>/', views.times, name='times'),
]
