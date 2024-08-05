from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from datetime import datetime
from django.http import Http404
from django.utils import timezone

from .models import User, Project, Task

@login_required
def HomePage(request):
    user = request.user

    # Obter projetos onde o usuário é membro
    user_projects = Project.objects.filter(members=user)

    # Inicializar um dicionário para armazenar as tarefas por projeto
    project_tasks = {}

    for project in user_projects:
        if project.created_by == user:
            # Se o usuário é o criador, obtém todas as tarefas do projeto
            tasks = Task.objects.filter(project=project)
        else:
            # Se o usuário não é o criador, obtém apenas as tarefas atribuídas ao usuário
            tasks = Task.objects.filter(project=project, assigned_to=user)

        # Adiciona as tarefas ao dicionário
        project_tasks[project] = tasks

    context = {
        'project_tasks': project_tasks,
    }
    return render(request, 'teamflow/main/index.html', context)

def LoginView(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        username = request.POST.get("email")
        password = request.POST.get("password")

        if not all([username, password]):
            messages.error(request, "Invalid username and/or password.")
            return HttpResponseRedirect(reverse('login'))
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return HttpResponseRedirect(reverse('login'))
    
    return render(request, 'teamflow/auth/login.html')


def LogoutView(request):
    if not request.user:
        return HttpResponseRedirect(reverse('login'))
    
    logout(request)
    return HttpResponseRedirect(reverse("home"))


def RegisterView(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('register'))
    
    if request.method == 'POST':
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if not all([username, email, password, confirm_password]):
            messages.error(request, "Error: Missing fields")
            return HttpResponseRedirect(reverse('register'))

        if confirm_password != password:
            messages.error(request, "Error: Passwords doesn't match")
            return HttpResponseRedirect(reverse('register'))

        if get_user_model().objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return HttpResponseRedirect(reverse('register'))
        
        try:   
            user = User(
                username = username,
                email = email,
            )
            user.set_password(password)
            user.save()
            return HttpResponseRedirect(reverse('login'))
        except Exception as e:
            messages.error(request, f"{e}")
            return HttpResponseRedirect(reverse('register'))
        

    return render(request, "teamflow/auth/register.html")


@login_required
def ProjectsView(requests):
    return render(requests, 'teamflow/main/projects.html')

@login_required
def CreateProjectView(request):
    if request.method == "POST":
        name = request.POST.get("name")
        start_date_str = request.POST.get("start_date")
        due_date_str = request.POST.get("due_date")
        description = request.POST.get("description")

        if not all([name, start_date_str, due_date_str, description]):
            messages.error(request, "Missing fields.")
            return HttpResponseRedirect(reverse('create_project'))

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return HttpResponseRedirect(reverse('create_project'))

        now = timezone.now().date()  

        if start_date < now:
            messages.error(request, "Start date cannot be in the past.")
            return HttpResponseRedirect(reverse('create_project'))
        elif due_date <= start_date:
            messages.error(request, "Due date must be after the start date.")
            return HttpResponseRedirect(reverse('create_project'))

        try:
            new_project = Project(
                name=name,
                start_date=start_date,
                due_date=due_date,
                description=description,
                created_by=request.user,
            )
            new_project.save()
            new_project.members.add(request.user)

            messages.success(request, "Project created successfully!")
            return HttpResponseRedirect(reverse('projects'))

        except Exception as e:
            messages.error(request, "An error occurred: " + str(e))
            print("An error occurred: ")
            return HttpResponseRedirect(reverse('create_project'))

    return render(request, "teamflow/projects/create_project.html")

@login_required
def SingleProjectPage(request, project_id):
    try:
        query_project = get_object_or_404(Project, pk=project_id)
    except Http404:
        messages.error(request, "Project not found.")
        return HttpResponseRedirect(reverse('home'))
    
    project_members = query_project.members.all()
    
    user = request.user

    if not query_project.members.filter(pk=user.pk).exists():
        messages.error(request, "Not allowed.")
        return HttpResponseRedirect(reverse('home'))

    members_with_tasks = []
    for member in project_members:
        tasks = Task.objects.filter(project=query_project, assigned_to=member)
        members_with_tasks.append({
            'member': member,
            'tasks': tasks
        })
    
    return render(request, "teamflow/projects/singleproject.html", {
        "project": query_project,
        "user": user,
        "members_with_tasks": members_with_tasks,
    })

@login_required
def add_member(request, project_id, email):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        user_to_add = get_object_or_404(get_user_model(), email=email)

        if request.user.id != project.created_by.id:
            messages.error(request, "Not allowed.")
            return HttpResponseRedirect('Home')

        if project.members.filter(email=email).exists():
            messages.error(request, "Member already added.")
            return HttpResponseRedirect(reverse('single_project', args=[project_id]))
        else:
            project.members.add(user_to_add)
            messages.success(request, "Member added.")
            return HttpResponseRedirect(reverse('single_project', args=[project_id]))
    else:    
        messages.error(request, "Not allowed.")
        return HttpResponseRedirect('Home')
    

@login_required
def Delete_Project(request, project_id):
    if request.method == "POST":
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            messages.error(request, "Error: Project not found")
            return HttpResponseRedirect(reverse('home'))

        if request.user.id != project.created_by.id:
            messages.error(request, "Not allowed")
            return HttpResponseRedirect(reverse('home'))
            
        project.delete()
        messages.success(request, "Project Deleted")
        return HttpResponseRedirect(reverse('projects'))

    messages.error(request, "Not allowed")
    return HttpResponseRedirect(reverse('home'))
    
@login_required
def Remove_member_from_project(request, project_id, member_id):
    if request.method == 'POST':
        # Obtém o projeto e o membro a partir dos IDs fornecidos
        project = get_object_or_404(Project, pk=project_id)
        member_to_remove = get_object_or_404(get_user_model(), pk=member_id)

        # Verifica se o usuário logado é o criador do projeto
        if request.user.id != project.created_by.id:
            messages.error(request, "Not Allowed")
            return redirect(reverse("single_project", args=[project_id]))

        # Verifica se o criador do projeto está tentando ser removido
        if member_to_remove.id == project.created_by.id:
            messages.error(request, "Can't remove the creator of the project")
            return redirect(reverse("single_project", args=[project_id]))

        # Verifica se o membro tem tarefas não terminadas
        unfinished_tasks = Task.objects.filter(project=project, assigned_to=member_to_remove, status__in=["Not started", "In progress"])

        if unfinished_tasks.exists():
            messages.error(request, "Cannot remove member: they have unfinished tasks.")
            return redirect(reverse('single_project', args=[project_id]))

        # Remove o membro do projeto
        project.members.remove(member_to_remove)
        
        messages.success(request, "Member removed successfully.")
        return redirect(reverse('single_project', args=[project_id]))

    # Se não for um POST, exibe uma mensagem de erro
    messages.error(request, "Invalid request method.")
    return redirect(reverse('single_project', args=[project_id]))


@login_required
def AssignTaskView(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        messages.error(request, "Error: Project does not exist.")
        return HttpResponseRedirect(reverse('projects'))

    if request.method == "POST":
        if request.user.id != project.created_by.id:
            messages.error(request, "Not allowed")
            return HttpResponseRedirect(reverse('home'))

        try:
            title = request.POST.get("title")
            description = request.POST.get("description")
            priority = request.POST.get("priority")
            due_date_str = request.POST.get("due_date")
            email = request.POST.get("assigned_to")

            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format.")
                return HttpResponseRedirect(reverse('single_project', args=[project_id]))

            if not all([title, description, priority, due_date_str, email]):
                messages.error(request, "Error: Missing field")
                return HttpResponseRedirect(reverse('single_project', args=[project_id]))

            project_start_date = project.start_date
            project_due_date = project.due_date

            if due_date < project_start_date or due_date > project_due_date:
                messages.error(request, "Error: Due date out of range")
                return HttpResponseRedirect(reverse('single_project', args=[project_id]))

            user = get_object_or_404(get_user_model(), email=email)
            
            if not project.members.filter(email=user.email).exists():
                messages.error(request, "Error: User is not in the project")
                return HttpResponseRedirect(reverse('single_project', args=[project_id]))

            new_task = Task(
                title=title,
                description=description,
                status="Not Started",
                priority=priority,
                due_date=due_date,
                assigned_to=user,
                project=project,
            )
            new_task.save()
            messages.success(request, "Task created successfully!")
            return HttpResponseRedirect(reverse('single_project', args=[project_id]))

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return HttpResponseRedirect(reverse('single_project', args=[project_id]))
        
    messages.error(request, "Not allowed")
    return HttpResponseRedirect(reverse('home'))


@login_required
def ChangeTaskStatus(request, task_id):
    if request.method == "POST":
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            messages.error(request, "Task, does not exist")
            return HttpResponseRedirect(reverse('home'))
    
        if request.user.id != task.assigned_to.id:
            messages.error(request, "You don't own the task")
            return HttpResponseRedirect(reverse('home'))
        
        new_status = request.POST.get("status")
        task.status = new_status
        task.save()
        return HttpResponseRedirect(reverse('home'))
    
    messages.error(request, "Not Allowed")
    return HttpResponseRedirect(reverse('home'))