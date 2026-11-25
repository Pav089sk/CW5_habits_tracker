from django.contrib import admin
from habits.models import Habit

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('action', 'founder', 'is_pleasant', 'periodicity', 'execution_time')
    list_filter = ('is_pleasant',)
    search_fields = ('action',)