from rest_framework import viewsets
from habits.models import Habit
from habits.serializers import HabitSerializer
from users.permissions import IsFounder


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для привычки"""
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsFounder]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Habit.objects.filter(founder=user)
        return Habit.objects.none()

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)


class PublicHabitsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Habit.objects.all()

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)