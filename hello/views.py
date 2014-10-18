from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.forms import UserCreationForm
import sys

from .models import Greeting

# Create your views here.
def index(request):
    return render(request, 'index.html', {'user': None, 'request': request})

def login(request):
    return render(request, 'login.html', {'user': None, 'request': request})
    
def logout(request):
    return render(request, 'index.html', {'user': None, 'request': request})
    
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
    if request.method == 'GET':
        params['form'] = UserCreationForm()
        return render(request, 'register.html', params)
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/account')
        params.update(csrf(request))
        params['nameInput'] = request.POST['name']
        params['emailInput'] = request.POST['email']
        params['emailError'] = "dam"
        params['form'] = UserCreationForm()
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


