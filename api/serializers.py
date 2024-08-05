from teamflow.models import (Project,
                             Task)

from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'username']
        

class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project"""

    class Meta:
        model = Project()
        fields = ['id', 'name', 'description', 'start_date', 'due_date', 'created_by', 'members']

