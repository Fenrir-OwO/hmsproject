from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, LoginForm, RoomBookingForm, ServiceBookingForm, FoodOrderForm
from .models import RoomBooking, FoodOrder, ServiceOrder, Employee, Billing, Payment, InventoryItem

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
            form.save() #INSERT INTO website_person (username, email, first_name, last_name, password) VALUES (...);
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
            room_booking.booked_by = request.user
            room_booking.total_price = room_booking.room.price * room_booking.num_nights
            room_booking.save() #INSERT INTO website_roombooking (room_id, booked_by_id, booking_date, num_nights, total_price) VALUES (...);

            booked_room = room_booking.room
            booked_room.is_available = False
            booked_room.save() # UPDATE website_room SET is_available = False WHERE id = [room_id];

            return redirect(reverse("index"))
    else:
        form = RoomBookingForm()
    return render(request, 'website/room_booking.html', {'form': form})

@login_required
def dashboard(request):
    is_employee = False
    if request.user.is_authenticated:
        try:
            employee = Employee.objects.get(person=request.user)
            is_employee = True
        except Employee.DoesNotExist:
            pass
    if is_employee:
        room_bookings = RoomBooking.objects.all() # SELECT * FROM website_roombooking;
        food_orders = FoodOrder.objects.all() # SELECT * FROM website_foodorder;
        service_orders = ServiceOrder.objects.all() # SELECT * FROM website_serviceorder;
        inventory_items = InventoryItem.objects.all() # SELECT * FROM website_inventoryitems;
        context = {
            'room_bookings': room_bookings,
            'food_orders': food_orders,
            'service_orders': service_orders,
            'inventory_items': inventory_items
        }
        return render(request, 'website/dashboard_employee.html', context)
    else:
        room_bookings = RoomBooking.objects.filter(booked_by=request.user) # SELECT * FROM website_roombooking WHERE booked_by_id = [current_user_id];
        food_orders = FoodOrder.objects.filter(ordered_by=request.user) # SELECT * FROM website_foodorder WHERE ordered_by_id = [current_user_id];
        service_orders = ServiceOrder.objects.filter(ordered_by=request.user) # SELECT * FROM website_serviceorder WHERE ordered_by_id = [current_user_id];

        context = {
            'room_bookings': room_bookings,
            'food_orders': food_orders,
            'service_orders': service_orders,
        }
        return render(request, 'website/dashboard.html', context=context)
@login_required
def checkout(request, booking_id):
    if request.user.is_authenticated:
        booking = get_object_or_404(RoomBooking, pk=booking_id)
        if booking.booked_by == request.user:
            booking.room.is_available = True
            booking.room.save() # UPDATE website_room SET is_available = True WHERE id = [room_id];
            booking.delete() # DELETE FROM website_roombooking WHERE id = [booking_id];
    return redirect('dashboard')

@login_required
def service_booking(request):
    if request.method == 'POST':
        form = ServiceBookingForm(request.POST)
        if form.is_valid():
            service_order = form.save(commit=False)
            service_order.ordered_by = request.user
            service_order.save() # INSERT INTO website_serviceorder (service_id, ordered_by_id, quantity) VALUES (...);
            return redirect('dashboard')
    form = ServiceBookingForm()
    return render(request, 'website/service_booking.html', {'form': form})

@login_required
def payment(request):
    unpaid_food_orders = FoodOrder.objects.filter(payment_status='unpaid')
    unpaid_service_orders = ServiceOrder.objects.filter(payment_status='unpaid')

    total_amount = sum(order.total_price for order in unpaid_food_orders) + sum(order.total_price for order in unpaid_service_orders)

    if request.method == 'POST':
        unpaid_food_orders.update(payment_status='paid') # UPDATE website_foodorder SET payment_status = 'paid' WHERE payment_status = 'unpaid';
        unpaid_service_orders.update(payment_status='paid') # UPDATE website_serviceorder SET payment_status = 'paid' WHERE payment_status = 'unpaid';
        return redirect('dashboard')

    context = {
        'unpaid_food_orders': unpaid_food_orders,
        'unpaid_service_orders': unpaid_service_orders,
        'total_amount': total_amount,
    }
    return render(request, 'website/payment.html', context)

@login_required
def food_order_view(request):
    if request.method == 'POST':
        form = FoodOrderForm(request.POST)
        if form.is_valid():
            food_order = form.save(commit=False)
            food_order.ordered_by = request.user
            food_order.save() # INSERT INTO website_foodorder (food_id, ordered_by_id, quantity) VALUES (...);
            return redirect('dashboard')
    form = FoodOrderForm()
    return render(request, 'website/food_order.html', {'form': form})
