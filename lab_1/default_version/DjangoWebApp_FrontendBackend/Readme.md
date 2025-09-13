# DjangoWebApp_FrontendBackend

## Overview
This project is a Dockerized Django web application (Frontend and Backend) built with Python, REST API, a MySQL database, JavaScript, HTML and CSS. 

* Easily manage users with a **drag-and-drop interface** to update their status.
* Quickly find users by first or last name with the **search feature**.
* Explore detailed film statistics through **dynamic visualizations**.
* View rental trends, earnings, and customer preferences with clear **charts and graphs**.
* Click on any **chart/graph** to **enlarge** it and explore detailed breakdowns of the visualized data.

Click on the image below to view the video featuring a screen recording of this project.

[![Watch the video](https://img.youtube.com/vi/E0KCLhKnEH0/maxresdefault.jpg)](https://youtu.be/E0KCLhKnEH0)

---

## Project Structure
```
DjangoWebApp_FrontendBackend/
├── assignment_project/       # Django project folder
│   ├── manage.py             # Django entry point
│   ├── assignment_project/   # Inner project folder (settings, wsgi, etc.)
│   │   ├── settings.py
│   │   ├── urls.py
│   ├── films                 # Films app for ./charts page
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── templates
│   │   │   ├── films
│   │   │   │   ├── dashboard.html
│   ├── users                 # Users app for ./user page
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── templates
│   │   │   ├── users
│   │   │   │   ├── user_list.html
│   ├── staticfiles           # Necessary static files including files enabling drag-and-drop functionality           
│   ├── templates
│   │   ├── main_page.html    # HTML page for main page which directs ./user and ./charts page via buttons
├── Dockerfile                # Docker image for the web service
├── docker-compose.yml        # Orchestration of web and database containers
├── .env                      # Environment variables
├── sql_files/                
│   ├── schema.sql            # Database schema
│   ├── data.sql              # Initial data
│   ├── requirements.txt      # Requirements for python virtual environment
```

---

## Build and Run Process

### Step 1: Build Docker Images
```bash
docker-compose build
```
### Step 2: Start Containers
```bash
docker-compose up -d
```
### Step 3: Verify Services
- Web service: [http://localhost:8000](http://localhost:8000)
- Main Page is accessible at http://localhost:8000
- ./user page is accessible at http://localhost:8000/users/user/
- ./charts page is accessible at http://localhost:8000/films/charts/

### Step 4: Stop Containers
```bash
docker-compose down
```

---
