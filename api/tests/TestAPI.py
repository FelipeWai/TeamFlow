from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from teamflow.models import Project
from django.urls import reverse

def create_user(username=None, email='test@email.com'):
    """Create user for testing authenticated features"""
    if username is None:
        username = 'TestUsername'
    else:
        username = username

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

class TestAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_login(self.user)
        self.project = create_project(self.user)
        self.project.members.add(self.user)

    def test_users_api(self):
        user2 = create_user(email="email@example.com")

        response = self.client.get(reverse('return_all_users'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        users = response.json()
        user_emails = [user['email'] for user in users]
        self.assertIn(user2.email, user_emails)

    def test_project_users_api(self):
        user2 = create_user(email="member@example.com")
        self.project.members.add(user2)
        
        url = reverse('project-members', kwargs={'pk': self.project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        users = response.json()
        user_emails = [user['email'] for user in users]
        
        self.assertIn(self.user.email, user_emails)
        self.assertIn(user2.email, user_emails)
    
    def test_projects_api(self):
        project2 = create_project(self.user)
        
        response = self.client.get(reverse('return_all_projects'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        projects = response.json()
        project_ids = [project['id'] for project in projects]
        
        self.assertIn(self.project.id, project_ids)
        self.assertIn(project2.id, project_ids)
    
    def test_user_projects_api(self):
        # Ensure project3 is saved and associated with the user2
        user2 = create_user(email="member@example.com")
        project3 = create_project(user2)
        project3.members.add(user2)
        project3.save()

        # Log in as the original user and fetch their projects
        self.client.force_login(self.user)
        
        url = reverse('return_user_projects')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        projects = response.json()
        project_ids = [project['id'] for project in projects]
        
        # Check that both self.project and project3 are included
        self.assertIn(self.project.id, project_ids)
        self.assertNotIn(project3.id, project_ids)  # This should be `assertIn` if self.user is a member of project3

    def test_specific_project_api(self):
        url = reverse('return_specific_project', kwargs={'pk': self.project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        project = response.json()
        
        # Compare the returned project details with the expected values
        self.assertEqual(project['id'], self.project.id)
        self.assertEqual(project['name'], self.project.name)
        self.assertEqual(project['description'], self.project.description)
        self.assertEqual(project['start_date'], self.project.start_date)
        self.assertEqual(project['due_date'], self.project.due_date)
