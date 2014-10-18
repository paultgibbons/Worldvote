from django.shortcuts import render
from django.http import HttpResponse
from django.core.context_processors import csrf
import sys
import re

from .models import Greeting

NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

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
    nameError = None
    emailError = None
    verifyError = None
    if not (name and NAME_RE.match(name)):
        nameError = 'Invalid Name'
    if not (pw and verify):
        verifyError = 'Invlaid Password'
    elif pw != verify:
        verifyError = 'Passwords do not match'
    if not (email and EMAIL_RE.match(email)):
        emailError = 'Invalid email'

    return nameError, verifyError, emailError    

# Create your views here.
def index(request):
    return render(request, 'index.html', {'user': None, 'request': request})

def login(request):
    return render(request, 'login.html', {'user': None, 'request': request})
    
def logout(request):
    return render(request, 'index.html', {'user': None, 'request': request})
    
def register(request):
    print >>sys.stderr, 'hello, James!'
    params = {
        'nameInput': '',
        'emailInput': '',
        'nameError': '',
        'emailError': '',
        'passwordError': '',
        'verifyError': '',
        'request': request
    }
    if request.method == 'GET':
        return render(request, 'register.html', params)
    elif request.method == 'POST':
        params.update(csrf(request))
        params['nameInput'] = request.POST['name']
        params['emailInput'] = request.POST['email']
        params['nameError'] = 'its not working'
        print params
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

    return render(request, 'db.html', {'greetings': greetings})


