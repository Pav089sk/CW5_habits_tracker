from rest_framework import serializers
from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            'id',
            'place',
            'time',
            'action',
            'founder',
            'is_pleasant',
            'reward',
            'linked_habit',
            'periodicity',
            'execution_time',
            'is_public'
        ]

    def validate(self, attrs):
        if attrs.get("reward") and attrs.get("linked_habit"):
            raise serializers.ValidationError("Исключите одновременный выбор связанной привычки и указания вознаграждения.")

        linked = attrs.get("linked_habit")
        if linked and not linked.is_pleasant:
            raise serializers.ValidationError("В связанные привычки могут попадать только приятные привычки.")

        if attrs.get("is_pleasant") and (attrs.get("reward") or attrs.get("linked_habit")):
            raise serializers.ValidationError("У приятной привычки нет награды и связанной привычки.")

        return attrs
