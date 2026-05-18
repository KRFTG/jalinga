from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('new/', views.create_booking, name='create_booking'),
    path('my/', views.booking_list, name='booking_list'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('get-slots/', views.get_slots, name='get_slots'),
    path('edit/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('calendar-data/', views.get_calendar_data, name='get_calendar_data'),
]