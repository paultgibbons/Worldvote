from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from datetime import datetime
import sys
import re

from .models import Greeting
from .models import User

NAME_RE = re.compile(r"^[ a-zA-Z0-9\s_-]+$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def alreadyExists(email):
    from django.db import connection, transaction
    cursor = connection.cursor()

    # Data modifying operation - commit required
    cursor.execute("SELECT email FROM hello_User WHERE email = '%s'" % email)
    
    return len(dictfetchall(cursor)) != 0

'''
Method to validate user form

Keyword Arguments:

name -- provided name
pw -- provided password 
verify -- provided verify password
email -- provided email

return:

nameError
verifyError
emailError

'''
def validate(name, pw, verify, email):
    nameError = ''
    emailError = ''
    verifyError = ''
    if not (name and NAME_RE.match(name)):
        nameError = 'Invalid Name'
    if not (pw and verify):
        verifyError = 'Invalid Password'
    elif pw != verify:
        verifyError = 'Passwords do not match'
    if not (email and EMAIL_RE.match(email)):
        emailError = 'Invalid email'
    if alreadyExists(email):
        emailError = 'Email already in use'

    return nameError, verifyError, emailError    

# Create your views here.
def index(request):
    params = { 'user': None, 'request' : request }
    if 'user_email' in request.session:
        params['user'] = User.objects.get(email=request.session['user_email'])
    return render(request, 'index.html', params)

def login(request):
    # TODO: redirect if user isn't None?
    params = {
        'user': None,
        'emailInput': '',
        'emailError': '',
        'passwordError': '',
        'request': request
    }
    params.update(csrf(request))
    if request.method == 'GET':
        return render(request, 'login.html', params)
    elif request.method == 'POST':
        email = request.POST['email']
        pw = request.POST['password']

        try:
            user = User.objects.get(email=email);
        except:
            user = None

        if user and pw == user.password:
            request.session['user_email'] = email
            return HttpResponseRedirect('/')

        params['emailInput'] = email
        params['emailError'] = 'Invalid username or password'
        params['passwordError'] = ''
        return render(request, 'login.html', params)
    
def logout(request):
    try:
        del request.session['user_email']
    except KeyError:
        pass
    return HttpResponseRedirect('/')
    
def register(request):
    params = {
        'user': None,
        'nameInput': '',
        'emailInput': '',
        'nameError': '',
        'emailError': '',
        'passwordError': '',
        'verifyError': '',
        'request': request
    }
    params.update(csrf(request))
    if request.method == 'GET':
        return render(request, 'register.html', params)
    elif request.method == 'POST':
        # validate request data
        name = request.POST['name']
        pw1 = request.POST['password1']
        pw2 = request.POST['password2']
        email = request.POST['email']
        image = request.POST['image']

        nameError, verifyError, emailError = validate(name, pw1, pw2, email)
        if nameError + verifyError + emailError == '':
            userModel = User(name=name, password=pw1, email=email, last_update=datetime.now(), score=0, image=image)
            userModel.save()
            return HttpResponseRedirect('/')
        params['nameInput'] = request.POST['name']
        params['emailInput'] = request.POST['email']
        params['nameError'] = nameError
        params['verifyError'] = verifyError
        params['emailError'] = emailError
        return render(request, 'register.html', params)
    
def account(request):
    return render(request, 'account.html', {'user': None, 'request': request})
    
def add(request):
    return render(request, 'add.html', {'user': None, 'request': request})

def profile(request):
    return render(request, 'profile.html', {'user': None, 'request': request})

# TODO: delete
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()
    users = User.objects.all()

    return render(request, 'db.html', {'greetings': greetings, 'users':users})


