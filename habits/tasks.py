import requests
from celery import shared_task
from django.conf import settings
from habits.models import Habit
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_habit_reminder():
    """
    Задача Celery: проверяет привычки и отправляет напоминания в Telegram.
    Учитывает периодичность и точное время выполнения.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    now = timezone.now()

    # Получаем все привычки, которые нужно проверить
    habits_to_check = Habit.objects.all()

    for habit in habits_to_check:
        # Проверяем, наступило ли время выполнения с учетом периодичности
        if (
                habit.time.hour == now.hour and
                habit.time.minute == now.minute and
                (now.date() - habit.founder.last_reminder_date).days % habit.periodicity == 0
        ):
            chat_id = habit.founder.telegram_chat_id
            message = (
                f"Напоминание: пора выполнить привычку!\n"
                f"Действие: {habit.action}\n"
                f"Место: {habit.place}\n"
                f"Продолжительность: {habit.execution_time} сек."
            )

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
            }

            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    # Обновляем дату последнего напоминания
                    habit.founder.last_reminder_date = now
                    habit.founder.save()
                    print(f"Сообщение отправлено для привычки {habit.id}")
                else:
                    print(f"Ошибка отправки: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Исключение при отправке: {e}")
