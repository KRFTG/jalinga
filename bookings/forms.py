from django import forms
from .models import Booking, StudioSchedule, StudioException
from django.utils import timezone

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_time', 'end_time', 'description']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'start_time': 'Начало',
            'end_time': 'Окончание',
            'description': 'Описание',
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if not start or not end:
            return cleaned_data

        now = timezone.now()
        if start < now:
            raise forms.ValidationError('Нельзя бронировать прошедшее время.')
        if end <= start:
            raise forms.ValidationError('Окончание должно быть позже начала.')

        # 1. Проверка рабочего дня и часов с учётом specific_date
        booking_date = start.date()
        day_of_week = start.isoweekday()

        # Сначала ищем специальный день на эту дату
        schedule = StudioSchedule.objects.filter(specific_date=booking_date).first()
        if not schedule:
            # Если нет спец. дня, берём обычное расписание по дню недели
            schedule = StudioSchedule.objects.filter(day_of_week=day_of_week).first()

        if not schedule:
            raise forms.ValidationError('В этот день студия не работает.')
        if not (schedule.start_time <= start.time() and end.time() <= schedule.end_time):
            raise forms.ValidationError('Бронирование должно полностью попадать в рабочие часы.')

        # 2. Проверка исключений (StudioException)
        exceptions = StudioException.objects.filter(date=booking_date)
        for exc in exceptions:
            if start.time() < exc.end_time and end.time() > exc.start_time:
                raise forms.ValidationError(f'Это время недоступно: {exc.reason or "исключение"}.')

        # 3. Конфликты с другими бронями (без изменений)
        conflicts = Booking.objects.filter(
            status__in=['booked', 'completed'],
            start_time__lt=end,
            end_time__gt=start
        )
        if self.instance.pk:
            conflicts = conflicts.exclude(pk=self.instance.pk)
        if conflicts.exists():
            raise forms.ValidationError('Это время уже занято.')

        return cleaned_data
    
class BookingConfirmForm(forms.Form):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Описание (необязательно)'}),
        label=''
    )
    file = forms.FileField(
        required=False,
        label='Прикрепить файл'
    )