from django.contrib import admin
from .models import Booking, StudioSchedule, StudioException
from .models import Equipment

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'start_time')
    search_fields = ('user__email', 'description')

@admin.register(StudioSchedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time')

@admin.register(StudioException)
class ExceptionAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'reason')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',)