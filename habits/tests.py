from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from habits.models import Habit

User = get_user_model()

HABITS_URL = '/api/habits/'
PUBLIC_URL = '/api/habits/public/'


def get_results(response):
    """Работает и с пагинацией (results), и без неё (просто список)."""
    data = response.data
    if isinstance(data, dict):
        return data.get('results', [])
    return data


def habit_payload(user, **overrides):
    data = {
        'founder': user.id,  # пока founder — writable поле сериализатора
        'action': 'Бегать',
        'place': 'Парк',
        'time': '08:00',
        'execution_time': 60,
        'periodicity': 1,
    }
    data.update(overrides)
    return data


class HabitValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='pass')
        self.client.force_authenticate(user=self.user)

    def test_periodicity_max_limit(self):
        """Нельзя реже 1 раза в 7 дней."""
        response = self.client.post(HABITS_URL, habit_payload(self.user, periodicity=8))
        self.assertEqual(response.status_code, 400)
        self.assertIn('periodicity', response.data)

    def test_execution_time_max_limit(self):
        """Время выполнения не больше 120 секунд."""
        response = self.client.post(HABITS_URL, habit_payload(self.user, execution_time=121))
        self.assertEqual(response.status_code, 400)
        self.assertIn('execution_time', response.data)

    def test_reward_and_linked_habit_exclusive(self):
        """Нельзя одновременно награду и связанную привычку."""
        pleasant = Habit.objects.create(
            founder=self.user,
            action='Ванна',
            place='Дом',
            time='21:00',
            execution_time=30,
            periodicity=1,
            is_pleasant=True,
        )
        response = self.client.post(HABITS_URL, habit_payload(
            self.user, reward='Чашка чая', linked_habit=pleasant.id
        ))
        self.assertEqual(response.status_code, 400)

    def test_linked_habit_must_be_pleasant(self):
        """В связанные попадают только приятные привычки."""
        useful = Habit.objects.create(
            founder=self.user,
            action='Прогулка',
            place='Улица',
            time='18:00',
            execution_time=30,
            periodicity=1,
        )
        response = self.client.post(HABITS_URL, habit_payload(
            self.user, linked_habit=useful.id
        ))
        self.assertEqual(response.status_code, 400)

    def test_pleasant_habit_cannot_have_reward(self):
        """У приятной привычки нет награды и связанной привычки."""
        response = self.client.post(HABITS_URL, habit_payload(
            self.user, is_pleasant=True, reward='Чашка чая'
        ))
        self.assertEqual(response.status_code, 400)


class HabitPermissionsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@example.com', password='pass')
        self.other = User.objects.create_user(email='other@example.com', password='pass')

        self.client_owner = APIClient()
        self.client_owner.force_authenticate(user=self.owner)
        self.client_other = APIClient()
        self.client_other.force_authenticate(user=self.other)

        self.habit = Habit.objects.create(
            founder=self.owner,
            action='Утренняя зарядка',
            place='Дом',
            time='07:00',
            execution_time=60,
            periodicity=1,
        )

    def test_owner_sees_own_habit(self):
        response = self.client_owner.get(HABITS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.habit.id, [h['id'] for h in get_results(response)])

    def test_other_user_does_not_see_private_habit(self):
        response = self.client_other.get(HABITS_URL)
        self.assertEqual(response.status_code, 200)
        ids = [h['id'] for h in get_results(response)]
        self.assertNotIn(self.habit.id, ids)

    def test_owner_can_edit_own_habit(self):
        response = self.client_owner.patch(
            f'{HABITS_URL}{self.habit.id}/', {'action': 'Зарядка 2'}, format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_edit_foreign_habit(self):
        response = self.client_other.patch(
            f'{HABITS_URL}{self.habit.id}/', {'action': 'Взломано'}, format='json'
        )
        self.assertEqual(response.status_code, 404)


class PublicHabitsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='pub@example.com', password='pass')
        self.public_habit = Habit.objects.create(
            founder=self.owner,
            action='Медитация',
            place='Парк',
            time='06:00',
            execution_time=60,
            periodicity=1,
            is_public=True,
        )
        self.private_habit = Habit.objects.create(
            founder=self.owner,
            action='Секретная привычка',
            place='Дом',
            time='23:00',
            execution_time=60,
            periodicity=1,
        )

    def test_anonymous_sees_public_habits(self):
        response = APIClient().get(PUBLIC_URL)
        self.assertEqual(response.status_code, 200)
        ids = [h['id'] for h in get_results(response)]
        self.assertIn(self.public_habit.id, ids)

    def test_private_habit_not_in_public_list(self):
        response = APIClient().get(PUBLIC_URL)
        ids = [h['id'] for h in get_results(response)]
        self.assertNotIn(self.private_habit.id, ids)

    def test_public_habit_is_read_only(self):
        client = APIClient()
        client.force_authenticate(user=self.owner)
        response = client.patch(f'{PUBLIC_URL}{self.public_habit.id}/', {'action': 'X'}, format='json')
        self.assertEqual(response.status_code, 405)
