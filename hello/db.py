import MySQLdb

"""
class User(models.Model):
    name = models.CharField(max_length=64)
    password = models.CharField(max_length=256)
    email = models.CharField(max_length=64)
    last_update = models.DateTimeField()
    score = models.IntegerField()
    image = models.FileField(upload_to='.')
    imgurl = models.CharField(max_length=16)

class Vote(models.Model):
    voter = models.CharField(max_length=64)
    votee = models.CharField(max_length=64)
    last_update = models.DateTimeField()
    direction = models.IntegerField()
"""

def create_user_table():
    pass

def create_vote_table():
    pass

def get_db():
    db = MySQLdb.connect('engr-cpanel-mysql.engr.illinois.edu', 'cjzhang2_cs411', r',-uE%lt*d@4a', 'cjzhang2_cs411')
    return db
