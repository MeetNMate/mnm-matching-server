from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('matching_result/', views.matching_result),
]