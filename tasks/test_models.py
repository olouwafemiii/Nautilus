from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Tasks

User = get_user_model()

class TaskModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name="Test",
            last_name="User",
        )

        self.task = Tasks.objects.create(
            title='Test Task',
            description='This is a test task.',
            due_date='2025-03-01',
            status='pending',
            owner=self.user
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'This is a test task.')
        self.assertEqual(self.task.due_date, '2025-03-01')
        self.assertEqual(self.task.status, 'pending')
        self.assertEqual(self.task.owner, self.user)

    def test_task_str(self):
        self.assertEqual(str(self.task), 'Test Task')

    def test_task_update(self):
        self.task.status = 'completed'
        self.task.save()
        self.assertEqual(self.task.status, 'completed')

    def test_task_deletion(self):
        task_id = self.task.id
        self.task.delete()
        with self.assertRaises(Tasks.DoesNotExist):
            Tasks.objects.get(id=task_id)
