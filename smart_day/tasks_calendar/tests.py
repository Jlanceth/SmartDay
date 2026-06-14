from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Tasks


class SmartDaySystemTests(TestCase):

    def setUp(self):
        """
        Предустановка данных: выполняется автоматически перед запуском каждого теста.
        Создаем тестового пользователя, который будет использоваться в сценариях.
        """
        self.username = "testuser"
        self.password = "secure_password_123"
        self.user = User.objects.create_user(
            username=self.username, 
            password=self.password, 
            email="test@smartday.ru"
        )
        
        self.login_url = '/users/login/'
        self.create_task_url = reverse('tasks_calendar:create')

    def test_user_login(self):
        """
        1. Тестирование аутентификации пользователя.
        """
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_create_task(self):
        """
        2. Тестирование валидации формы и создания стандартной задачи.
        Проверяет работу слоя ModelForm и сохранение записи в PostgreSQL.
        """
        self.client.login(username=self.username, password=self.password)
        now = timezone.now()
        start = now + timezone.timedelta(hours=1)
        end = now + timezone.timedelta(hours=2)
        response = self.client.post(self.create_task_url, {
            'title': 'Тестовая задача в помещении',
            'description': 'Описание тестовой задачи',
            'task_type': 'study',
            'is_outdoor': False,  # Задача внутри помещения
            'location': 'Университет, ауд. 200',
            'start_time': start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end.strftime('%Y-%m-%dT%H:%M'),
            'need_remind': False,
            'remind_days_before': 1
        })
        self.assertEqual(response.status_code, 302)
        task_exists = Tasks.objects.filter(title='Тестовая задача в помещении', user=self.user).exists()
        self.assertTrue(task_exists)

    def test_create_event(self):
        """
        3. Тестирование создания уличного события, требующего адаптивной рекомендации.
        """
        self.client.login(username=self.username, password=self.password)
        now = timezone.now()
        start = now + timezone.timedelta(hours=3)
        end = now + timezone.timedelta(hours=5)
        response = self.client.post(self.create_task_url, {
            'title': 'Спортивная тренировка на стадионе',
            'description': 'Бег на открытом воздухе',
            'task_type': 'sport',
            'is_outdoor': True,
            'location': 'Городской стадион',
            'start_time': start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end.strftime('%Y-%m-%dT%H:%M'),
            'need_remind': True,
            'remind_days_before': 2
        })
        self.assertEqual(response.status_code, 302)
        created_task = Tasks.objects.get(title='Спортивная тренировка на стадионе', user=self.user)
        self.assertTrue(created_task.is_outdoor)
        self.assertTrue(created_task.need_remind)
        self.assertEqual(created_task.remind_days_before, 2)












    