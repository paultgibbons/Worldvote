import binascii
import hashlib
import time

import MySQLdb as mysql

def get_db():
    try:
        return mysql.connect('engr-cpanel-mysql.engr.illinois.edu',
            'cjzhang2_cs411', r'', 'cjzhang2_cs411')
    except:
        pass
    return None

def create_table_user():
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE Users (
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
        cursor.execute("""
            CREATE TABLE Votes (
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
    dk = hashlib.pbkdf2_hmac('sha256', password, '', 100000)
    return binascii.hexlify(dk)

def user_register(name, password, email, image):
    # validation


    # hash password, convert image to base64, get current time
    hashed_password = get_hashed_password(password)
    image_base64 = '' # TODO
    epoch = int(time.time())

    db = get_db()
    
    try:
        cursor = db.cursor()

        # find next user id


        # add user
        cursor.execute("""
            INSERT INTO Users (id, name, password, email, last_update, image)
            VALUES (%d, %s, %s, %s, %d, %s);
            """ % (user_id, name, hashed_pasword, email, epoch, image_base64))
    except:
        pass
    db.close()

def user_login(email, password):
    db = get_db()
    if db is None:
        return -1

    try:
        cursor = db.cursor()



    pass


