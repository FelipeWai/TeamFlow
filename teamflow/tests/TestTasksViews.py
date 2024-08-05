from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from teamflow.models import Project, Task
from datetime import timedelta
from django.utils import timezone


def create_user(username=None, email='test@email.com'):
    """Create user for testing authenticated features"""
    if username is None:
        username = 'TestUsername'
    else:
        username=username

    password = 'testpass123'
    
    new_user = get_user_model().objects.create(
        username=username,
        email=email
    )
    new_user.set_password(password)
    new_user.save()

    return new_user

def create_project(user):
    today = timezone.now().date()
    after_tomorrow = today + timedelta(days=2)

    name = "Test Project"
    description = "Test Project Description"
    start_date = today.strftime("%Y-%m-%d")
    due_date = after_tomorrow.strftime("%Y-%m-%d")

    new_project = Project.objects.create(
        name=name,
        description=description,
        start_date=start_date,
        due_date=due_date,
        created_by=user
    )

    return new_project

def create_task(user, project):
    title="Task"
    description="Task Description"
    status="Not Started"
    priority="Low"
    due_date=timezone.now().date() + timedelta(days=2)

    new_task = Task.objects.create(
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        assigned_to=user,
        project=project
    )

    return new_task



def check_message(response, message):
    """Test if message is in the response"""
    messages = list(get_messages(response.wsgi_request))
    return any(msg.message == f"{message}" for msg in messages)

def AssignTaskURL(arg):
    return reverse('assign_task', args=[arg])

def SingleProjectURL(arg):
    return reverse('single_project', args=[arg])

def ChangeStatusURL(arg):
    return reverse('update_status', args=[arg])


class TestAssignTaskView(TestCase):
    """Tests for assigning view"""

    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

        self.project = create_project(self.user)
        self.project.members.add(self.user)


    def test_project_not_found_error(self):
        projects = Project.objects.all()
        test_id = projects.last().id + 1
        response = self.client.post(AssignTaskURL(test_id))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects'))
        self.assertTrue(check_message(response, "Error: Project does not exist."))

    def test_not_creator_request_error(self):
        new_user = create_user(email='email@example.com')
        self.client.force_login(new_user)

        response = self.client.post(AssignTaskURL(self.project.id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(check_message(response, "Not allowed"))        

    def test_missing_fields(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
        payload = {
            'title': 'Test Title',
            'description': 'Test Description',
            'priority': '',
            'due_date': tomorrow.strftime("%Y-%m-%d"),
            'assigned_to': ''
        }

        response = self.client.post(AssignTaskURL(self.project.id), payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, SingleProjectURL(self.project.id))
        self.assertTrue(check_message(response, "Error: Missing field"))

    def test_invalid_date_format(self):
        payload = {
            'title': 'Test Title',
            'description': 'Test Description',
            'priority': 'Low',
            'due_date': '2024/08/04',
            'assigned_to': 'test@email.com'
        }
        
        response = self.client.post(AssignTaskURL(self.project.id), payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, SingleProjectURL(self.project.id))
        self.assertTrue(check_message(response, "Invalid date format."))

    def test_due_date_out_of_range_error(self):
        wrong_date = timezone.now().date() + timedelta(days=20)
        payload = {
            'title': 'Test Title',
            'description': 'Test Description',
            'priority': 'Low',
            'due_date': wrong_date.strftime("%Y-%m-%d"),
            'assigned_to': 'test@email.com'
        }

        response = self.client.post(AssignTaskURL(self.project.id), payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, SingleProjectURL(self.project.id))
        self.assertTrue(check_message(response, "Error: Due date out of range"))

    def test_user_not_in_project_error(self):
        new_user = create_user(email='email@example.com')
        tomorrow = timezone.now().date() + timedelta(days=1)
        payload = {
            'title': 'Test Title',
            'description': 'Test Description',
            'priority': 'Low',
            'due_date': tomorrow.strftime("%Y-%m-%d"),
            'assigned_to': new_user.email
        }

        response = self.client.post(AssignTaskURL(self.project.id), payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, SingleProjectURL(self.project.id))
        self.assertTrue(check_message(response, "Error: User is not in the project"))


    def test_create_task_success(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
        payload = {
            'title': 'Test Title',
            'description': 'Test Description',
            'priority': 'Low',
            'due_date': tomorrow.strftime("%Y-%m-%d"),
            'assigned_to': self.user.email
        }

        response = self.client.post(AssignTaskURL(self.project.id), payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, SingleProjectURL(self.project.id))
        self.assertTrue(check_message(response, "Task created successfully!"))

        task = Task.objects.get(project=self.project, assigned_to=self.user)
        self.assertIsNotNone(task)
        self.assertEqual(task.status, "Not Started")
        self.assertNotEqual(task.status, "In progress")

    def test_user_not_authenticated_error(self):
        self.client.get(reverse('logout'))
        response = self.client.post(AssignTaskURL(self.project.id))

        self.assertEqual(response.status_code, 302)

    def test_get_request_error(self):
        response = self.client.get(AssignTaskURL(self.project.id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(check_message(response, "Not allowed"))


class TestChangeTaskStatusView(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

        self.project = create_project(self.user)
        self.project.members.add(self.user)

        self.task = create_task(self.user, self.project)
    
    def test_get_request_error(self):
        response = self.client.get(ChangeStatusURL(self.task.id))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(check_message(response, "Not Allowed"))

    def test_task_id_doesnt_exist(self):
        test_id = Task.objects.all().last().id + 1
        response = self.client.post(ChangeStatusURL(test_id))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(check_message(response, "Task, does not exist"))

    def test_not_owner_request_error(self):
        new_user = create_user(email="email@example.com")
        self.client.force_login(new_user)
        response = self.client.post(ChangeStatusURL(self.task.id))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(check_message(response, "You don't own the task"))

    def test_post_request_success(self):
        payload = {'status': 'In Progress'}
        response = self.client.post(ChangeStatusURL(self.task.id), payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'In Progress')