from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import CustomUser


class Habit(models.Model):
    founder = models.ForeignKey(CustomUser,
                                on_delete=models.CASCADE,
                                related_name='habits',
                                verbose_name='Владелец')
    place = models.CharField(max_length=255, verbose_name='Место выполнения')
    time = models.TimeField(verbose_name='Время выполнения')
    action = models.CharField(max_length=200, verbose_name='Действие')
    is_pleasant = models.BooleanField(default=False, verbose_name='Приятная привычка')
    linked_habit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_to',
                                     verbose_name='Связанная привычка')
    periodicity = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(7)], verbose_name='Периодичность (в днях)')
    reward = models.CharField(max_length=200, blank=True, null=True, verbose_name='Вознаграждение')
    execution_time = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)],verbose_name='Продолжительность (в секундах)')
    is_public = models.BooleanField(default=False, verbose_name='Публичная')

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ('id',)

    def __str__(self):
        return self.action