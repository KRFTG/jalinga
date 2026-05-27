from django.contrib import admin
from .models import Booking, StudioSchedule, StudioException
from .models import Equipment
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.utils.html import format_html
from .models import Booking, StudioSchedule, StudioException, Equipment, GroupMember
from accounts.models import CustomUser

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'status_colored', 'created_at')
    list_filter = ('status', 'start_time')
    search_fields = ('user__email', 'description')
    actions = ['make_completed']

    def status_colored(self, obj):
        colors = {
            'booked': '#0056b3',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Статус'

    def make_completed(self, request, queryset):
        updated = queryset.filter(status='booked').update(status='completed')
        self.message_user(request, f'{updated} броней отмечены как завершённые.')
    make_completed.short_description = 'Отметить завершёнными выбранные брони'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_bookings'] = Booking.objects.count()
        extra_context['active_bookings'] = Booking.objects.filter(status='booked').count()
        extra_context['total_users'] = CustomUser.objects.count()
        extra_context['equipment_usage'] = Equipment.objects.annotate(
            usage_count=Count('booking')
        ).order_by('-usage_count')
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('chart-data/', self.admin_site.admin_view(self.chart_data), name='booking_chart_data'),
        ]
        return custom_urls + urls

    def chart_data(self, request):
        today = timezone.now().date()
        days = int(request.GET.get('days', 7))
        labels = []
        values = []
        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%d.%m'))
            values.append(Booking.objects.filter(start_time__date=day).count())
        return JsonResponse({'labels': labels, 'values': values})

admin.site.register(Booking, BookingAdmin)
admin.site.register(StudioSchedule)
admin.site.register(StudioException)
admin.site.register(Equipment)
admin.site.register(GroupMember)