from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage, name='home'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('register/', views.RegisterView, name="register"),

    path('projects/', views.ProjectsView, name='projects'),
    path('projects/create/', views.CreateProjectView, name='create_project'),
    path('projects/<int:project_id>/', views.SingleProjectPage, name='single_project'),
    path('projects/<int:project_id>/tasks/create/', views.AssignTaskView, name='assign_task'),
    path('projects/<int:project_id>/members/add/<str:email>/', views.add_member, name='add_member'),
    path('projects/<int:project_id>/members/remove/<int:member_id>/', views.Remove_member_from_project, name='remove_member'),
    path('projects/<int:project_id>/delete/', views.Delete_Project, name='delete_project'),
    
    path('tasks/update/<int:task_id>', views.ChangeTaskStatus, name='update_status'),
]