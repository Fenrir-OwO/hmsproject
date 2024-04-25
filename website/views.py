from django.shortcuts import render
from django.urls import path

# Create your views here.
def home_view(request):
    return render(request, 'index.html')
def room_view(request):
    return render(request, 'website/room.html')
def food_view(request):
    return render(request, 'website/food.html')
def service_view(request):
    return render(request, 'website/service.html')
def about_view(request):
    return render(request, 'website/about.html')