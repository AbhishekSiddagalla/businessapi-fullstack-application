# Integration of django(backend) with react(frontend)

## requirements 
for django install the following:
            
    pip install django, djangorestframework, djangorestframework-simplejwt django-cors-headers

## steps for backend application
create project name 

    django-admin startproject Business_API

create an application

    py manage.py startapp menu

add app name in settings and also add other names

    Business_API > settings

    INSTALLED_APPS = [ 'menu', 'rest_framework', 'rest_framework_simplejwt', 'corsheaders']

    MIDDLEWARE = [ 'corsheaders.middleware.CorsMiddleware'  ]

## Frontend
 install nodejs
 
open root directory create application for frontend

    npm create vite@latest frontend

select a framework → React

select a variant - JavaScript

navigate to frontend → cd frontend
    
    Business_API > frontend

install required packages by running the following command

    npm install

to start react server run the command

    npm run dev
