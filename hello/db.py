import base64
import binascii
import hashlib
import os.path
import time

import sys # TEMP

import MySQLdb as mysql

class Struct(object):
    pass

def get_db():
    try:
        return mysql.connect('engr-cpanel-mysql.engr.illinois.edu',
            'cjzhang2_cs411', r',-uE%lt*d@4a', 'cjzhang2_cs411')
    except:
        pass
    return None

def get_user_from_tuple(user_tuple):
    user = Struct()
    keys = ('id', 'name', 'password', 'email', 'last_update', 'score', 'image')
    for i in range(len(keys)):
        setattr(user, keys[i], user_tuple[i])
    return user

def create_table_user():
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE Users (
                id          INTEGER PRIMARY KEY,
                name        VARCHAR(64),
                password    CHAR(64),
                email       VARCHAR(64) UNIQUE,
                last_update INTEGER,
                score       INTEGER DEFAULT 0,
                image       MEDIUMTEXT
            );
            """)
    except:
        print 'create_table_user failed'
    db.close()

def create_table_vote():
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE Votes (
                voter       VARCHAR(64),
                votee       VARCHAR(64),
                last_update INTEGER,
                direction   INTEGER,
                PRIMARY KEY (voter, votee)
            );
            """)
    except:
        print 'create_table_vote failed'
    db.close()

def get_hashed_password(password):
    dk = hashlib.pbkdf2_hmac('sha256', password, 'DS1i.x8FpGKR', 100000)
    return binascii.hexlify(dk)

def get_base64_image(image):
    extension = os.path.splitext(image.name)[1][1:]
    data = base64.b64encode(image.read())
    return 'data:image/' + extension + ';base64,' + data

def user_register(name, password, email, image):
    # validation (should validate image too)

    # hash password, convert image to base64, get current time
    hashed_password = get_hashed_password(password)
    base64_image = get_base64_image(image)
    epoch = int(time.time())

    db = get_db()   # TODO: get_db error checking
    try:
        cursor = db.cursor()
        cursor.execute("SELECT MAX(id) FROM Users;")
        user_id = cursor.fetchone()[0]
        if not user_id:
            user_id = 1
        else:
            user_id += 1
        cursor.execute("""INSERT INTO Users (id, name, password, email, last_update, image)
            VALUES (%d, '%s', '%s', '%s', %d, '%s');
            """ % (user_id, name, hashed_password, email, epoch, base64_image))
        db.commit()
    except:
        db.rollback()
        print >> sys.stderr, sys.exc_info()[0]
        print >> sys.stderr, 'user_register failed'
        pass
    db.close()

def user_login(email): # TODO should also take password?
    db = get_db()
    if db is not None:
        try:
            cursor = db.cursor()
            cursor.execute("""
                SELECT *
                FROM Users
                WHERE email = '%s'
                """ % (email, ))
            user_tuple = cursor.fetchone()
            db.close() # TODO can refactor
            return get_user_from_tuple(user_tuple)
        except:
            pass
        db.close()
    return None

def user_by_id(user_id): # TODO THIS IS TEMP
    db = get_db()
    if db is not None:
        try:
            cursor = db.cursor()
            cursor.execute("""
                SELECT *
                FROM Users
                WHERE id = %d
                """ % (int(user_id), ))
            user_tuple = cursor.fetchone()
            db.close() # TODO can refactor
            return get_user_from_tuple(user_tuple)
        except:
            pass
        db.close()
    return None

def user_by_name(name): # TODO THIS IS TEMP
    db = get_db()
    if db is not None:
        try:
            cursor = db.cursor()
            cursor.execute("""
                SELECT *
                FROM Users
                WHERE name = '%s'
                """ % (name, ))
            user_tuple = cursor.fetchone()
            db.close() # TODO can refactor
            return get_user_from_tuple(user_tuple)
        except:
            pass
        db.close()
    return None

def user_delete(email):
    db = get_db()
    if db is not None:
        cursor = db.cursor()
        cursor.execute("DELETE FROM Users WHERE email = '%s'" % email)
        db.commit()
        db.close()

def user_reverse(user_id):

    pass

def user_upvote(voter_email, votee_email, direction):

    pass


def vote_create(voter, votee, timestamp, direction):
    db = get_db()
    if db is not None: # use with instead? for all
        try:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO Votes (voter, votee, last_update, direction)
                VALUES ('%s', '%s', %d, %d)
                """ % (voter, votee, timestamp, direction))
            db.commit()
        except:
            db.rollback()
            pass
        db.close()








