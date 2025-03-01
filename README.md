# Task_Manager API

## Overview

The Task_Manager API is a little project to handle users task management enabling them to create tasks and have a follow-up of it.

## Prerequisites

- **Python**: Ensure that Python is installed on your machine. Follow the [Python installation documentation](https://www.python.org/downloads/) for guidance.
- **pip**: Ensure that pip is installed. It is typically included with Python. Check your version with:
  ```bash
  pip --version

## File Structure

**manage.py**: Django's command-line utility for administrative tasks.
**task_manager/settings.py**: Settings for the Django project.
**task_manager/urls.py**: URL declarations for the Django project.
**tasks/models.py**: Models for the tasks app.
**tasks/views.py**: Views for the tasks app.
**tasks/serializers.py**: Serializers for the tasks app.
**tasks/filters.py**: Filters for the tasks app.
**tasks/tests.py**: Tests for the tasks app.

## Setup

### Step 1: Clone the Repository
    ```bash
    git clone git@github.com:olouwafemiii/Nautilus.git
    cd Nautilus
    ```
### Step 2: Create a Virtual Environment and Install Dependencies
  ```bash
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activatee`
    pip install -r requirements.txt
  ```
### Step 3: Create a `.env`(Environment Variables) file in the `Task_Manager` folder with the following content (you can adjust the values as needed):
    ```env
      # .env
      # secret_key
      SECRET_KEY=your_secret_key
      DEBUG=True
      
      # Emails Configs
      EMAIL_HOST=smtp-relay.brevo.com
      EMAIL_PORT=587
      EMAIL_HOST_USER=your_brevo_user_mail
      EMAIL_HOST_PASSWORD=your_password

      DB_NAME=your_database_name
    ```

### Step 4: Run migrations and create a superuser:
    ```bash
    python manage.py makemigrations accounts tasks
    python manage.py migrate
    python manage.py createsuperuser
    ```

### Step 5: Launch the server
    ```bash
    python manage.py runserver
    ```

### Step 5. Access the application at `http://127.0.0.1:8000/`.

## API Endpoints

- **POST /users/register**: Register a new user.
- **POST /users/login**: Authenticate a user and obtain a token.
- **GET /tasks**: Retrieve a list of Task_Manager.
- **POST /tasks**: Create a new Learning Nugget.
- **GET /tasks/:id**: Retrieve a specific Learning Nugget.
- **PUT /tasks/:id**: Update a specific Learning Nugget.
- **DELETE /tasks/:id**: Delete a specific Learning Nugget.


## Run Unitests

  ```bash
    python manage.py test 'folder name(accounts/tasks)'
  ```

---
