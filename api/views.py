from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from teamflow.models import (Project,
                             Task)
from . import serializers


class ReturnUsersAPI(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReturnProjectsAPI(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReturnSpecificProjectAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    lookup_field = 'pk' 


class ReturnUserProjectsAPI(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(Q(created_by=user)| Q(members=user)).distinct()
    
class ReturProjectUsersAPI(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        project_id = self.kwargs['pk'] 
        try:
            project = Project.objects.get(pk=project_id)
            return project.members.all()
        except Project.DoesNotExist:
            return get_user_model().objects.none()