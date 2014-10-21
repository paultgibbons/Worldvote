from datetime import datetime
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db import connection, transaction
from django.shortcuts import render
from django.shortcuts import render_to_response
import json
import os
import os.path
import re
import sys
from .models import User

NAME_RE = re.compile(r"^[ a-zA-Z0-9\s_-]+$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
PASSWORD_RE = re.compile(r'^.{4,}')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def alreadyExists(email):
    cursor = connection.cursor()

    # Data modifying operation - commit required
    cursor.execute("SELECT email FROM hello_User WHERE email = '%s'" % email)
    
    return len(dictfetchall(cursor)) != 0

def validate(name, pw, verify, email):
    nameError = ''
    emailError = ''
    verifyError = ''
    if not (name and NAME_RE.match(name)):
        nameError = 'Invalid Name'
    if not (pw and verify):
        verifyError = 'Invalid Password'
    elif not PASSWORD_RE.match(pw):
        verifyError = 'Password too short'
    elif pw != verify:
        verifyError = 'Passwords do not match'
    if not (email and EMAIL_RE.match(email)):
        emailError = 'Invalid email'
    if alreadyExists(email):
        emailError = 'Email already in use'

    return nameError, verifyError, emailError    

# Create your views here.
def index(request):
    # params = { 'user': None, 'request' : request }
    # if 'user_email' in request.session:
    #     params['user'] = User.objects.get(email=request.session['user_email'])
    # return render(request, 'index.html', params)
    return HttpResponseRedirect('/register')

def search(request):
    query = request.GET['query']
    cursor = connection.cursor()
    try:
        # search ny email
        user = User.objects.get(email=query)
        return HttpResponseRedirect('/%d' % int(user.id))
    except:
        pass
    try:
        # search by name
        user = User.objects.get(name__iexact=query)
        return HttpResponseRedirect('/%d' % int(user.id))
    except:
        pass

    return HttpResponseRedirect('/%d' % 20000000000)

def login(request):
    if 'user_email' in request.session:
        return HttpResponseRedirect('/account')

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
            return HttpResponseRedirect('/account')

        params['emailInput'] = email
        params['emailError'] = 'Invalid username or password'
        params['passwordError'] = ''
        return render(request, 'login.html', params)
    
def logout(request):
    try:
        del request.session['user_email']
    except KeyError:
        pass
    return HttpResponseRedirect('/login')
    
def register(request):
    if 'user_email' in request.session:
        return HttpResponseRedirect('/account')

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
        image = request.FILES['image']

        nameError, verifyError, emailError = validate(name, pw1, pw2, email)
        if nameError + verifyError + emailError == '':
            userModel = User(name=name, password=pw1, email=email, last_update=datetime.now(), score=0, image=None, imgurl='')
            userModel.save()
            src = str(userModel.id) + os.path.splitext(image.name)[1]
            image.name = src
            userModel.imgurl = src
            userModel.image = image
            userModel.save()
            return HttpResponseRedirect('/login')
        params['nameInput'] = request.POST['name']
        params['emailInput'] = request.POST['email']
        params['nameError'] = nameError
        params['verifyError'] = verifyError
        params['emailError'] = emailError
        return render(request, 'register.html', params)
    
def account(request):
    params = { 'user': None, 'request' : request }
    if 'user_email' in request.session:
        params['user'] = User.objects.get(email=request.session['user_email'])
        return render(request, 'account.html', params)
    else:
        return HttpResponseRedirect('/login')
    
def add(request):
    params = { 'user': None, 'request' : request }
    if 'user_email' in request.session:
        params['user'] = User.objects.get(email=request.session['user_email'])
        return render(request, 'add.html', params)
    else:
        return HttpResponseRedirect('/login')

def profile(request, userid):
    params = { 'user': None, 'request' : request }
    if 'user_email' in request.session:
        params['user'] = User.objects.get(email=request.session['user_email'])

    try:
        params['person'] = User.objects.get(id=userid)
    except:
        params['person'] = None

    return render(request, 'profile.html', params)

def delete(request):
    email = 'error'
    try:
        email = request.session['user_email']
        del request.session['user_email']
    except KeyError:
        pass
    user = User.objects.get(email = email)
    try:
        os.remove(BASE_DIR + '/../mediafiles/'+user.imgurl)
    except:
        pass

    cursor = connection.cursor()
    cursor.execute("DELETE FROM hello_User WHERE email = '%s'" % email)
    return HttpResponseRedirect('/login')

def reverse(request):
    email = 'error'
    try:
        email = request.session['user_email']
    except KeyError:
        pass
    cursor = connection.cursor()
    user = User.objects.get(email=email)
    cursor.execute("UPDATE hello_User SET name = '%s' WHERE id = %d" % (user.name[::-1], user.id))
    return HttpResponseRedirect('/account')

def upvote(request):
    voter = '';
    try:
        voter = request.session['user_email']
    except:
        return HttpResponseRedirect('/login')
    votee = request.POST['email']

    cursor = connection.cursor()
    score = cursor.execute("SELECT score FROM hello_User WHERE email = '%s'" % votee).fetchone()[0]
    if votee != voter:
        score += 1
        cursor.execute("UPDATE hello_User SET score = %d WHERE email = '%s'" % (score, votee))
    else:
        score = False
    response_data = {}
    response_data['score'] = score
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def downvote(request):
    voter = '';
    try:
        voter = request.session['user_email']
    except:
        return HttpResponseRedirect('/login')
    votee = request.POST['email']
    
    cursor = connection.cursor()
    score = cursor.execute("SELECT score FROM hello_User WHERE email = '%s'" % votee).fetchone()[0]
    if votee != voter:
        score -= 1
        cursor.execute("UPDATE hello_User SET score = %d WHERE email = '%s'" % (score, votee))
    else:
        score = False
    response_data = {}
    response_data['score'] = score
    return HttpResponse(json.dumps(response_data), content_type="application/json")


# TODO: delete
def db(request):
    users = User.objects.all()

    return render(request, 'db.html', {'request':request,'users':users})


