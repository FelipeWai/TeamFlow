from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.ReturnUsersAPI.as_view(), name='return_all_users'),

    path('projects/', views.ReturnProjectsAPI.as_view(), name='return_all_projects'),
    path('projects/user/', views.ReturnUserProjectsAPI.as_view(), name='return_user_projects'),
    path('projects/<int:pk>/', views.ReturnSpecificProjectAPI.as_view(), name='return_specific_project'),
    
    path('project/<int:pk>/users/', views.ReturProjectUsersAPI.as_view(), name='project-members'),
]
