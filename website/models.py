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
"""
CREATE TABLE website_person (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE
);
"""
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
    
"""
CREATE TABLE website_phonenumber (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    number VARCHAR(15),
    FOREIGN KEY (person_id) REFERENCES website_person(id) ON DELETE CASCADE
);
"""
class PhoneNumber(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    number = models.CharField(max_length=15)

    def __str__(self):
        return self.number
"""
CREATE TABLE website_employee (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT UNIQUE,
    employee_id VARCHAR(20) UNIQUE,
    salary INT,
    role VARCHAR(100),
    FOREIGN KEY (person_id) REFERENCES website_person(id) ON DELETE CASCADE
);
"""
class Employee(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    salary = models.IntegerField(null=True)
    role = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.person.first_name} {self.person.last_name} - {self.employee_id}'
"""
CREATE TABLE website_room (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(50) UNIQUE,
    num_beds INT,
    room_type VARCHAR(20),
    price DECIMAL(10, 2),
    is_available BOOLEAN DEFAULT TRUE
);
"""
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
"""
CREATE TABLE website_roombooking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT,
    booked_by_id INT,
    booking_date DATE DEFAULT CURRENT_DATE,
    num_nights INT,
    total_price DECIMAL(10, 2),
    FOREIGN KEY (room_id) REFERENCES website_room(id) ON DELETE CASCADE,
    FOREIGN KEY (booked_by_id) REFERENCES website_person(id) ON DELETE CASCADE
);
"""
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
"""
CREATE TABLE website_food (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_item_number VARCHAR(50) UNIQUE,
    description TEXT,
    price DECIMAL(10, 2),
    food_type VARCHAR(10)
);
"""
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
"""
CREATE TABLE website_foodorder (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_status VARCHAR(10),
    food_id INT,
    ordered_by_id INT,
    quantity INT,
    order_date DATE DEFAULT CURRENT_DATE,
    total_price INT,
    FOREIGN KEY (food_id) REFERENCES website_food(id) ON DELETE CASCADE,
    FOREIGN KEY (ordered_by_id) REFERENCES website_person(id) ON DELETE CASCADE
);
"""
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
"""
CREATE TABLE website_service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_id VARCHAR(10) UNIQUE,
    description TEXT,
    price DECIMAL(10, 2),
    service_type VARCHAR(20)
);
"""
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
"""
CREATE TABLE website_serviceorder (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_status VARCHAR(10),
    service_id INT,
    ordered_by_id INT,
    quantity INT,
    order_date DATE DEFAULT CURRENT_DATE,
    total_price INT,
    FOREIGN KEY (service_id) REFERENCES website_service(id) ON DELETE CASCADE,
    FOREIGN KEY (ordered_by_id) REFERENCES website_person(id) ON DELETE CASCADE
);
"""
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
"""
CREATE TABLE website_payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10, 2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    food_order_id INT,
    service_order_id INT,
    FOREIGN KEY (user_id) REFERENCES website_person(id) ON DELETE CASCADE,
    FOREIGN KEY (food_order_id) REFERENCES website_foodorder(id) ON DELETE SET NULL,
    FOREIGN KEY (service_order_id) REFERENCES website_serviceorder(id) ON DELETE SET NULL
);
"""
class Payment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    food_order = models.ForeignKey(FoodOrder, on_delete=models.SET_NULL, null=True, blank=True)
    service_order = models.ForeignKey(ServiceOrder, on_delete=models.SET_NULL, null=True, blank=True)
"""
CREATE TABLE website_billing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10, 2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10),
    FOREIGN KEY (user_id) REFERENCES website_person(id) ON DELETE CASCADE
);
"""
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
"""
CREATE TABLE website_inventoryitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    quantity INT DEFAULT 0
);
"""
class InventoryItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Quantity: {self.quantity})"