from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from teamflow.models import Project
from datetime import timedelta, date
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
    name = "Test Project"
    description = "Test Project Description"
    start_date = "2024-07-10"
    due_date = "2024-08-01"

    new_project = Project.objects.create(
        name=name,
        description=description,
        start_date=start_date,
        due_date=due_date,
        created_by=user
    )

    return new_project


def check_message(response, message):
    """Test if message is in the response"""

    messages = list(get_messages(response.wsgi_request))
    return any(msg.message == f"{message}" for msg in messages)



CREATE_PROJECT_URL = reverse('create_project')
PROJECTS_PAGE_URL = reverse('projects')
SINGLE_PROJECT_PAGE = reverse('single_project', args=[1])
def delete_project_page(arg):
    return reverse('delete_project', args=[arg])



class TestCreateProjectView(TestCase):

    """Tests for all projects views"""

    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

    def test_non_authenticated_user(self):
        self.client.get(reverse('logout'))

        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)

        response = self.client.get(CREATE_PROJECT_URL)
        self.assertEqual(response.status_code, 302)
        

    def test_create_project_success(self):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        # start_date_str = today.strftime('%Y-%m-%d')
        # due_date_str = tomorrow.strftime('%Y-%m-%d')
        payload = {
            'name': 'Test Project',
            'start_date': today.strftime("%Y-%m-%d"),
            'due_date': tomorrow.strftime("%Y-%m-%d"),
            'description': 'Test Project Description'
        }

        response = self.client.post(CREATE_PROJECT_URL, payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, PROJECTS_PAGE_URL)
        self.assertTrue(check_message(response, "Project created successfully!"))

        projects = Project.objects.filter(created_by=self.user)
        self.assertEqual(projects.count(), 1)
        
        project = projects.first()
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.start_date, date.fromisoformat(today.strftime("%Y-%m-%d")))
        self.assertEqual(project.due_date, date.fromisoformat(tomorrow.strftime("%Y-%m-%d")))
        self.assertEqual(project.description, 'Test Project Description')

    def test_missing_fields_error(self):
        tz = timezone.get_current_timezone()
        today = timezone.now().astimezone(tz).date()
        tomorrow = today + timedelta(days=1)

        payload = {
            'name': 'Test Project',
            'start_date': tomorrow.strftime("%Y-%m-%d"),  # Amanhã
            'description': 'Test Project Description'
        }

        response = self.client.post(CREATE_PROJECT_URL, payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, CREATE_PROJECT_URL)
        self.assertTrue(check_message(response, "Missing fields."))


    def test_wrong_date_format_error(self):
        payload = {
            'name': 'Test Project',
            'start_date': '02/08/2024', 
            'due_date': '10/08/2024',
            'description': 'Test Project Description'
        }

        response = self.client.post(CREATE_PROJECT_URL, payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, CREATE_PROJECT_URL)
        self.assertTrue(check_message(response, "Invalid date format."))

    def test_start_date_in_past_error(self):
        tz = timezone.get_current_timezone()

        yesterday_start = (timezone.now() - timedelta(days=1)).astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)

        today_end = timezone.now().astimezone(tz).replace(hour=23, minute=59, second=59, microsecond=999999)

        payload = {
            'name': 'Test Project',
            'start_date': yesterday_start.strftime("%Y-%m-%d"),
            'due_date': today_end.strftime("%Y-%m-%d"),
            'description': 'Test Project Description'
        }

        response = self.client.post(CREATE_PROJECT_URL, payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, CREATE_PROJECT_URL)
        self.assertTrue(check_message(response, "Start date cannot be in the past."))
    
    def test_due_date_before_start_date_error(self):
        tz = timezone.get_current_timezone()

        today_start = timezone.now().astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)

        yesterday_end = (timezone.now() - timedelta(days=1)).astimezone(tz).replace(hour=23, minute=59, second=59, microsecond=999999)

        payload = {
            'name': 'Test Project',
            'start_date': today_start.strftime("%Y-%m-%d"),
            'due_date': yesterday_end.strftime("%Y-%m-%d"),
            'description': 'Test Project Description'
        }

        response = self.client.post(CREATE_PROJECT_URL, payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, CREATE_PROJECT_URL)
        self.assertTrue(check_message(response, "Due date must be after the start date."))

    def test_due_date_equal_to_start_date_not_allowed(self):
        today = timezone.now().date()

        payload = {
            'name': 'Test Project',
            'start_date': today.strftime("%Y-%m-%d"),
            'due_date': today.strftime("%Y-%m-%d"),
            'description': 'Test Project Description'
        }
        response = self.client.post(CREATE_PROJECT_URL, payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, CREATE_PROJECT_URL)
        self.assertTrue(check_message(response, "Due date must be after the start date."))



class TestProjectsPage(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

        self.project = create_project(self.user)
        self.project.members.add(self.user)


    def test_get_request_success(self):
        response = self.client.get(SINGLE_PROJECT_PAGE, args=[self.project.id])

        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_error(self):
        self.client.get(reverse('logout'))
        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)

        response = self.client.get(SINGLE_PROJECT_PAGE, args=[self.project.id])
        self.assertEqual(response.status_code, 302)

    def test_user_not_member_redirected_error(self):
        new_user = create_user(email='newuser@example.com')

        self.client.force_login(new_user)
        response = self.client.get(SINGLE_PROJECT_PAGE, args=[self.project.id])

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(check_message(response, "Not allowed."))

    def test_invalid_project_id_error(self):
        projects = Project.objects.all()
        test_id = projects.last().id + 10

        response = self.client.get(reverse('single_project', args=[test_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(check_message(response, "Project not found."))
        self.assertRedirects(response, reverse('home'))



class TestDeleteProject(TestCase):
    """Test for Delete project View"""
    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

        self.project = create_project(self.user)
        self.project.members.add(self.user)

    def test_get_request_error(self):
        response = self.client.get(delete_project_page(self.project.id))
        self.assertRedirects(response, reverse('home'))

    def test_unauthorized_user_post_error(self):
        self.client.get(reverse('logout'))
        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)

        response = self.client.post(delete_project_page(self.project.id))
        self.assertEqual(response.status_code, 302)

        project = Project.objects.get(pk=self.project.id)
        self.assertIsNotNone(project)

    def test_non_existing_id_error(self):
        projects = Project.objects.all()
        test_id = projects.last().id + 10

        response = self.client.post(delete_project_page(test_id))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(check_message(response, "Error: Project not found"))

    def test_not_creator_error(self):
        new_user = create_user(email="email@example.com")
        self.client.force_login(new_user)

        response = self.client.post(delete_project_page(self.project.id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(check_message(response, "Not allowed"))

    def test_delete_success(self):
        response = self.client.post(delete_project_page(self.project.id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects')) 
        self.assertTrue(check_message(response, "Project Deleted"))