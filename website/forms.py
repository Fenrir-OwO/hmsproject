from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Person, Room, RoomBooking, Service, ServiceOrder

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    phone_number = forms.CharField(max_length=15, help_text='Enter your phone number.')

    class Meta:
        model = Person
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class RoomBookingForm(forms.ModelForm):
    room_type = forms.ChoiceField(choices=Room.ROOM_TYPES, required=False)

    def __init__(self, *args, **kwargs):
        super(RoomBookingForm, self).__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(is_available=True)

    class Meta:
        model = RoomBooking
        fields = ['room', 'num_nights', 'booking_date']

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['service', 'quantity', 'order_date']
    