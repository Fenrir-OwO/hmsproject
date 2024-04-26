from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.contrib.auth import get_user_model
from django.utils import timezone

class PersonManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class Person(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, blank=True, related_name='persons')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='persons')

    objects = PersonManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
class PhoneNumber(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    number = models.CharField(max_length=15)

    def __str__(self):
        return self.number
class Employee(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    salary = models.IntegerField(null=True)
    role = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.person.first_name} {self.person.last_name} - {self.employee_id}'
    
class Room(models.Model):
    STANDARD_SINGLE = 'standard_single'
    PREMIUM_SINGLE = 'premium_single'
    STANDARD_DOUBLE = 'standard_double'
    PREMIUM_DOUBLE = 'premium_double'
    LUXURY_FAMILY = 'luxury_family'

    ROOM_TYPES = [
        (STANDARD_SINGLE, 'Standard Single Room'),
        (PREMIUM_SINGLE, 'Premium Single Room'),
        (STANDARD_DOUBLE, 'Standard Double Room'),
        (PREMIUM_DOUBLE, 'Premium Double Room'),
        (LUXURY_FAMILY, 'Luxury Family Room'),
    ]

    room_number = models.CharField(max_length=50, unique=True)
    num_beds = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)  # Default to available

    def __str__(self):
        return f"{self.room_number} ({self.room_type})"

class RoomBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booked_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    booking_date = models.DateField(default=timezone.now)
    num_nights = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.room.price * self.num_nights
        super(RoomBooking, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.room.room_number} ({self.room.room_type}) - {self.booked_by.username}"
    
class Food(models.Model):
    PIZZA = 'pizza'
    BURGER = 'burger'
    PASTA = 'pasta'
    
    FOOD_TYPES = [
        (PIZZA, 'Pizza'),
        (BURGER, 'Burger'),
        (PASTA, 'Pasta'),
    ]
    
    food_item_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    food_type = models.CharField(max_length=10, choices=FOOD_TYPES)
    def __str__(self):
        return f"{self.food_item_number} - {self.food_type}"

class FoodOrder(models.Model):
    PAID = 'paid'
    UNPAID = 'unpaid'
    PAYMENT_STATUS_CHOICES = [
        (PAID, 'Paid'),
        (UNPAID, 'Unpaid'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=UNPAID)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateField(default=timezone.now)
    total_price = models.IntegerField()
    def __str__(self):
        return f"{self.food.food_type} - {self.ordered_by.username}"
    def save(self, *args, **kwargs):
        self.total_price = self.food.price * self.quantity
        super(FoodOrder, self).save(*args, **kwargs)   
class Service(models.Model):
    KIDS_PLAYING_ZONE = 'kids_playing_zone'
    GYM = 'gym'
    SWIMMING_POOL = 'swimming_pool'
    GAMING_ZONE = 'gaming_zone'
    BICYCLE_RIDES = 'bicycle_rides'
    TOURIST_BUS = 'tourist_bus'

    SERVICE_TYPES = [
        (KIDS_PLAYING_ZONE, 'Kids Playing Zone'),
        (GYM, 'Gym'),
        (SWIMMING_POOL, 'Swimming Pool'),
        (GAMING_ZONE, 'Gaming Zone'),
        (BICYCLE_RIDES, 'Bicycle Rides'),
        (TOURIST_BUS, 'Tourist Bus'),
    ]
    service_id = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)

    def __str__(self):
        return f"{self.service_id} - {self.service_type}"
class ServiceOrder(models.Model):
    PAID = 'paid'
    UNPAID = 'unpaid'
    PAYMENT_STATUS_CHOICES = [
        (PAID, 'Paid'),
        (UNPAID, 'Unpaid'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=UNPAID)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateField(auto_now_add=True)
    total_price = models.IntegerField(null=True)
    def save(self, *args, **kwargs):
        self.total_price = self.service.price * self.quantity
        super(ServiceOrder, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.service.service_type} - {self.ordered_by.username}"

class Payment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    food_order = models.ForeignKey(FoodOrder, on_delete=models.SET_NULL, null=True, blank=True)
    service_order = models.ForeignKey(ServiceOrder, on_delete=models.SET_NULL, null=True, blank=True)
class Billing(models.Model):
    PAID = 'paid'
    UNPAID = 'unpaid'

    BILL_STATUS_CHOICES = [
        (PAID, 'Paid'),
        (UNPAID, 'Unpaid'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=BILL_STATUS_CHOICES, default=UNPAID)