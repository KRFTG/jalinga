from django import forms
from .models import Booking
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
        # 1. не в прошлом
        if start < now:
            raise forms.ValidationError('Нельзя бронировать прошедшее время.')
        if end <= start:
            raise forms.ValidationError('Окончание должно быть позже начала.')

        # 2. рабочий день и часы
        from .models import StudioSchedule
        day_of_week = start.isoweekday()
        schedule = StudioSchedule.objects.filter(day_of_week=day_of_week)
        if not schedule.exists():
            raise forms.ValidationError('В этот день студия не работает.')
        start_time = start.time()
        end_time = end.time()
        ok = any(s.start_time <= start_time and end_time <= s.end_time for s in schedule)
        if not ok:
            raise forms.ValidationError('Время должно попадать в рабочие часы.')

        # 3. исключения
        from .models import StudioException
        exc_list = StudioException.objects.filter(date=start.date())
        for exc in exc_list:
            if start_time < exc.end_time and end_time > exc.start_time:
                raise forms.ValidationError(f'Это время недоступно: {exc.reason or "исключение"}.')

        # 4. конфликты
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