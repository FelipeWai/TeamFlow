from django.test import TestCase
from django.contrib.auth import get_user_model
from teamflow.models import Project, Task
from datetime import datetime


def create_user():
    username = 'TestUsername'
    email = 'test@email.com'
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

def create_task(user, project):
    task = Task.objects.create(
            title = 'TestTitle',
            description = 'Test Description',
            status = 'Done',
            priority = 'Big',
            due_date = '2024-08-10',
            assigned_to = user,
            project = project
        )
    
    return task


class TestModels(TestCase):
    """Test creating models"""

    def test_user_creation(self):
        """Test creating User"""
        username = 'TestUsername'
        email = 'test@email.com'
        password = 'testpass123'
        new_user = get_user_model().objects.create(
            username=username,
            email=email
        )
        new_user.set_password(password)
        new_user.save()

        num_of_users = get_user_model().objects.all().count()
        self.assertEqual(num_of_users, 1)
        
        user = get_user_model().objects.get(email=email)
        self.assertTrue(user.check_password(password))



    def test_project_creation(self):
        """Test creating Project"""
        user = create_user()

        name = "Test Project"
        description = "Test Project Description"
        start_date = "2024-07-10"
        due_date = "2024-08-01"

        new_project = Project.objects.create(
            name=name,
            description=description,
            start_date=start_date,
            due_date=due_date,
            created_by=user,
        )

        num_of_projects = Project.objects.all().count()
        self.assertEqual(num_of_projects, 1)

        num_of_members = new_project.members.all().count()
        self.assertEqual(num_of_members, 0)


    def test_task_creation(self):
        """Test creating a task"""
        user = create_user()
        project = create_project(user)
        Task.objects.create(
            title = 'TestTitle',
            description = 'Test Description',
            status = 'Done',
            priority = 'Big',
            due_date = '2024-08-10',
            assigned_to = user,
            project = project
        )

        num_of_tasks = Task.objects.all().count()
        self.assertEqual(num_of_tasks, 1)
        
        task = Task.objects.get(title='TestTitle', project=project)
        self.assertEqual(task.assigned_to, user)