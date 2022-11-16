# Yatube
## _Yet another social network_
This is the project of pretty simple social network. It was made to get the hang of building projects with Django, to understand interaction between database, models, views, ulrs and templates, creating forms, customizing the admin site. The project is covered with tests that are made with pytest.
Unauthenticated user can register/login, browse feed on main page and profiles of authors. Authenticated user can also create and edit posts, leave comments, follow other authors, change password.
# Prerequisites
Python version 3.7
Pip 19.2.3
# Setting up
First you need to clone the repo into the directory on your machine. After you need to create and activate virtual environment, install required packages and create local database.
```
python3 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```
If you wish to take a look at the project in browser - run local server and open http://127.0.0.1:8000/ 
``` 
python manage.py runserver
```
To create superuser (you will be asked information required for user registration)
```
python manage.py createsuperuser
```

# To-do 
- email password reset
- change fbv to cbv