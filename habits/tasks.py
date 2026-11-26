import requests
from celery import shared_task
from django.conf import settings
from habits.models import Habit
from django.utils import timezone

@shared_task
def send_habit_reminder():
    """
    Задача Celery: проверяет привычки и отправляет напоминания в Telegram.
    Запускается по расписанию.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not bot_token or not chat_id:
        print("Ошибка: TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не заданы!")
        return

    now = timezone.now()
    habits_to_notify = Habit.objects.filter(
        time__hour=now.hour,
        time__minute=now.minute
    )

    for habit in habits_to_notify:
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
                print(f"Сообщение отправлено для привычки {habit.id}")
            else:
                print(f"Ошибка отправки: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Исключение при отправке: {e}")
