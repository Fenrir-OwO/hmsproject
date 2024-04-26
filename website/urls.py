from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='index'),
    path('room/', views.room_view, name='room'),
    path('food/', views.food_view, name='food'),
    path('service/', views.service_view, name='service'),
    path('about/', views.about_view, name='about'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('room_booking/', views.room_booking, name='room_booking'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('service_booking/', views.service_booking, name='service_booking'),

]