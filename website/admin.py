from django.contrib import admin
from .models import Person, Employee, Room, RoomBooking, Food, FoodOrder, Service, ServiceOrder, Payment, InventoryItem

# Register your models here.
admin.site.register(Person)
admin.site.register(Employee)
admin.site.register(Room)
admin.site.register(RoomBooking)
admin.site.register(Food)
admin.site.register(FoodOrder)
admin.site.register(Service)
admin.site.register(ServiceOrder)
admin.site.register(Payment)
admin.site.register(InventoryItem)
