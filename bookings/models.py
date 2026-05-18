from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

class Booking(models.Model):
    class Status(models.TextChoices):
        BOOKED = 'booked', _('Забронировано')
        COMPLETED = 'completed', _('Завершено')
        CANCELLED = 'cancelled', _('Отменено')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('пользователь')
    )
    start_time = models.DateTimeField(_('начало'))
    end_time = models.DateTimeField(_('конец'))
    description = models.TextField(_('описание'), blank=True)
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.BOOKED
    )
    created_at = models.DateTimeField(_('создана'), auto_now_add=True)

    class Meta:
        verbose_name = _('бронирование')
        verbose_name_plural = _('бронирования')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} — {self.start_time:%d.%m.%Y %H:%M}'


class BookingFile(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('бронирование')
    )
    file = models.FileField(_('файл'), upload_to='booking_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('файл бронирования')
        verbose_name_plural = _('файлы бронирований')


class StudioSchedule(models.Model):
    day_of_week = models.IntegerField(_('день недели (1=Пн, 7=Вс)'))
    start_time = models.TimeField(_('время начала работы'))
    end_time = models.TimeField(_('время окончания работы'))

    class Meta:
        verbose_name = _('рабочие часы')
        verbose_name_plural = _('рабочие часы')

    def __str__(self):
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        return f'{days[self.day_of_week - 1]} {self.start_time}–{self.end_time}'


class StudioException(models.Model):
    date = models.DateField(_('дата'))
    start_time = models.TimeField(_('начало'))
    end_time = models.TimeField(_('конец'))
    reason = models.TextField(_('причина'), blank=True)

    class Meta:
        verbose_name = _('исключение в расписании')
        verbose_name_plural = _('исключения в расписании')

    def __str__(self):
        return f'{self.date} {self.start_time}–{self.end_time} ({self.reason})'


class GroupMember(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='group_members',
        verbose_name=_('бронирование')
    )
    full_name = models.CharField(_('ФИО'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('телефон'), max_length=20, blank=True)

    class Meta:
        verbose_name = _('участник группы')
        verbose_name_plural = _('участники группы')

    def __str__(self):
        return f'{self.full_name or self.email} ({self.booking})'