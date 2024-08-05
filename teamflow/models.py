from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    start_date = models.DateField()
    due_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    members = models.ManyToManyField(User, related_name='joined_projects')

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1024)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    due_date = models.DateField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
