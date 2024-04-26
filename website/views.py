from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, LoginForm, RoomBookingForm

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
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('index'))
            else:
                form.add_error(None, "Invalid username or password.")

    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect(reverse('index'))
@login_required
def room_booking(request):
    if request.method == 'POST':
        form = RoomBookingForm(request.POST)
        if form.is_valid():
            room_booking = form.save(commit=False)
            room_booking.booked_by = request.user  # Assuming user is logged in
            room_booking.total_price = room_booking.room.price * room_booking.num_nights
            room_booking.save()

            # Mark the booked room as unavailable
            booked_room = room_booking.room
            booked_room.is_available = False
            booked_room.save()

            return redirect(reverse("index"))
    else:
        form = RoomBookingForm()
    return render(request, 'website/room_booking.html', {'form': form})