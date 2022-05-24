# Python-sample-code

Python sample project code

## Setting Up Local Environment

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/taufikcrest/python-sample-code.git
$ cd python-sample-code
```

Create a virtual environment to install dependencies in and activate it:
```sh
python -m venv venv
```
For windows to activate ENV:
```sh
venv\scripts\activate
```
For Mac/Ubuntu to activate ENV:
```sh
source env/bin/activate
```
Then install the dependencies:
```sh
(env)$ pip install -r requirements.txt
```

Once `pip` has finished downloading the dependencies:
```sh
(env)$ python manage.py migrate
(env)$ python manage.py runserver
```

Here is a postman collection to check APIs
```sh
https://www.getpostman.com/collections/5da452be97c6acdbbc9b
```

You can create super user for admin access
```sh
(env)$ python manage.py createsuperuser
```

After creating super user you can hit this URL and access of admin panel.
```sh
http://127.0.0.1:8000/admin/
```

