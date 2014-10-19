from django.db import models

class User(models.Model):
    name = models.CharField(max_length=64)
    password = models.CharField(max_length=256)
    email = models.CharField(max_length=64, primary_key=True)
    last_update = models.DateTimeField()
    score = models.IntegerField()
    image = models.ImageField(upload_to='/media/')

class Vote(models.Model):
    voter = models.CharField(max_length=64)
    votee = models.CharField(max_length=64)
    last_update = models.DateTimeField()
    direction = models.IntegerField()
