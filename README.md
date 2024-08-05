
# TeamFlow CS50W Final Project

A simple and concise website for teams to work together on projects


## Distinctiveness and Complexity

#### Unique Purpose and Functionality

TeamFlow is a web application focused on project management, offering features distinct from those covered in other course projects. Unlike the pizza project, social network, and e-commerce, which have more specific and limited scopes, TeamFlow provides a comprehensive platform for creating and managing collaborative projects. Users can create projects, add team members, and organize tasks, fostering a more integrated environment for teamwork.

#### Project and Task Management

While the social network project focuses on social interaction and the e-commerce project on commerce, TeamFlow is designed to facilitate team collaboration and project organization. It allows users to create projects, add members, and set up tasks with different priorities and statuses, offering a project management system not addressed in the other course projects.

#### Technical Complexity

TeamFlow employs Django for the backend, incorporating multiple models to represent projects, users, and tasks. This level of data modeling surpasses that of the previous projects. Additionally, JavaScript is used to implement dynamic frontend features, such as real-time updates of tasks and projects, adding an extra layer of complexity and interactivity.


## Documentation

For the Final Project I've decided to create 2 apps, one for the api and other for the app templates, static files, views, models, urls and admin site configuration. 


## TeamFlow APP

This app is used as the main app, having the templates, static files, main urls, views and models

### Database

The database used was the sqlite3 default database created by django by means of fast and light queries.

### Models

#### User model
The User model extends Django’s built-in AbstractUser class to customize user authentication by using email as the "USERNAME_FIELD" instead of the default username.

#### Project model
The Project model is designed to manage key aspects of project management within the TeamFlow application. It provides fields for identifying the project, setting timelines, and tracking team involvement, ensuring comprehensive project oversight and collaboration.

#### Task model
The Task model is designed to manage and track tasks within a project, capturing essential details such as title, description, status, priority, due date, assignment, and project association. This model ensures that tasks are clearly defined, assigned, and monitored, facilitating effective project management and team collaboration within the TeamFlow application.

![Models Image](Readme_images\Models_Image.png)

### URLS

The URL configuration defines the routing for various views in the application, including home page navigation, user authentication, and project management.


![Urls Image](Readme_images\Urls_Image.png)


### Views

**Authentication:**
* `HomePage`: Displays personalized project view after login.
* `LoginView`, `LogoutView`, `RegisterView`: Handle user authentication.

**Project Management:**
* `ProjectsView`, `CreateProjectView`, `SingleProjectPage`, `add_member`, `Delete_Project`: Manage project creation, viewing, and membership.

**Task Management:**
* `Remove_member_from_project`, `AssignTaskView`, `ChangeTaskStatus`: Handle task assignment and status updates.

### Templates
The templates for this project are organized into three main folders: main, auth, and projects. Each template extends a base layout.html file, which provides a consistent structure across the site. Individual templates then define their own specific content and titles.

For dynamic content, such as the single project page and the home page, Django’s templating engine is utilized to render data directly from the database. This includes using template tags and loops to display information retrieved from database queries.

In contrast, for pages like the projects overview, JavaScript and API calls are employed to fetch and present data asynchronously. This approach enhances the user experience by providing more interactive and responsive content.

You can explore these templates and static assets in the templates and static folders, respectively.
## API Documentation

For this project, I utilized the Django Rest Framework (DRF) to build a robust API. DRF enabled the retrieval of various types of data, including project details, registered users, project members, and a comprehensive list of all projects within the application. This data is then consumed by JavaScript on the front end to dynamically populate and update the user interface. This integration allows for a responsive and interactive user experience, as JavaScript handles data rendering and updates in real-time based on the API responses.


#### Return all users

```http
  GET /api/users/
```


#### Return all projects

```http
  GET /api/projects/
```


#### Return Single project

```http
  GET /api/projects/<int:pk>/
```
"pk" is the id from the project you want to search


#### Return users for a single project

```http
  GET /api/projects/<int:pk>/users/
```

"pk" is the id from the project you want to search
## Testing

Tests have been implemented for both the TeamFlow application and the API to ensure functionality and reliability.

### TeamFlow App

Tests for the TeamFlow app are organized in the `tests` folder within the `teamflow` directory. This includes:

- **Models**: Tests to verify the correctness of the application’s data models.
- **Authentication**: Tests for user authentication processes, including registration and login.
- **Views**: Tests for the various views to ensure they render correctly and handle user interactions as expected.

### API

For the API, tests have been conducted to verify the accuracy and completeness of the information retrieved from the endpoints. This includes:

- Testing the responses from the API endpoints to ensure they return the expected data formats and content.

These tests help ensure that both the application and API function as intended, providing a robust and reliable user experience.

## Running the application

To run the TeamFlow web application, follow these steps:

1. **Install Dependencies**

   Make sure you have the required packages installed. You can install them using the provided `requirements.txt` file by running:

   ```bash
   pip install -r requirements.txt

This will install the necessary packages, including:

- Django
- Django Rest Framework (DRF)
- Pytz

2. **Start the Development Server**

Navigate to the main project directory and start the development server with:

```bash
    python manage.py runserver
```
Once the server is running, you can access the application by opening your web browser and visiting http://127.0.0.1:8000/.

## Screenshots

![Login Page](Readme_images\Login_Page_Image.png)
![Register Page](Readme_images\Register_Page.png)
![Index Page](Readme_images\Index_Image.png)
![Projects Image](Readme_images\Projects_Image.png)
![Single Project Image](Readme_images\Single_Project_Page.png)
![Add Member](Readme_images\Add_Member_Image.png)
![Assign Task](Readme_images\Assign_Task_Image.png)
