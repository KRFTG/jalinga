from .models import Booking, Equipment
from accounts.models import CustomUser
from django.db.models import Count

def admin_dashboard_stats(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status='booked').count()
    total_users = CustomUser.objects.count()
    equipment_usage = Equipment.objects.annotate(
        usage_count=Count('booking')
    ).order_by('-usage_count')
    return {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_users': total_users,
        'equipment_usage': equipment_usage,
    }