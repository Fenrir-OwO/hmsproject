from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='index'),
    path('room/', views.room_view, name='room'),
    path('food/', views.food_view, name='food'),
    path('service/', views.service_view, name='service'),
    path('about/', views.about_view, name='about')
]