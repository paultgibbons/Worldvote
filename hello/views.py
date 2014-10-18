from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

# Create your views here.
def index(request):
    return render(request, 'index.html', {'user': None, 'request': request})

def login(request):
    return render(request, 'login.html', {'user': None, 'request': request})
    
def logout(request):
    return render(request, 'logout.html', {'user': None, 'request': request})
    
def register(request):
    return render(request, 'register.html', {'user': None, 'request': request})
    
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


