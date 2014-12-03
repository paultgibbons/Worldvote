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
from .db import get_db, user_register, user_login
from .db import get_image, user_by_id, vote_create, user_by_name, user_delete
from .db import get_hashed_password, get_user_from_tuple, join_query
import time
from .models import User, Vote

NAME_RE = re.compile(r"^[ a-zA-Z0-9\s_-]+$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
PASSWORD_RE = re.compile(r'^.{4,}')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def alreadyExists(email):
    db = get_db()
    cursor = db.cursor()


    # Data modifying operation - commit required
    cursor.execute("SELECT email FROM Users WHERE email = '%s'" % email)
    matches = len(cursor.fetchall())
    db.close()
    
    return matches != 0

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

def index(request):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users ORDER BY score DESC LIMIT 10")
    users = cursor.fetchall()
    temp = []
    for user in users:
        temp.append(get_user_from_tuple(user))
    users = temp

    user = None
    if 'user_email' in request.session:
        user = user_login(request.session['user_email'])
    return render(request, 'index.html', {'request':request, 'users':users, 'user':user})

def search(request):
    query = request.GET['query']
    cursor = connection.cursor()
    try:
        # search ny email
        user = user_login(query)#User.objects.get(email=query)
        return HttpResponseRedirect('/%d' % int(user.id))
    except:
        pass
    try:
        # search by name
        #user = User.objects.get(name__iexact=query)
        user = user_by_name(query)#User.objects.get(email=query)
        return HttpResponseRedirect('/%d' % int(user.id))
    except:
        pass

    return HttpResponseRedirect('/%d' % 20000000000)

def unpack_user(user):
    response_data = {}
    if user is None:
        response_data['id'] = -1
        response_data['name'] = ''
        response_data['password'] = ''
        response_data['email'] = ''
        response_data['last_update'] = 0
        response_data['score'] = 0
        response_data['image'] = ''
    else:
        response_data['id'] = user.id
        response_data['name'] = user.name
        response_data['password'] = user.password
        response_data['email'] = user.email
        response_data['last_update'] = user.last_update
        response_data['score'] = user.score
        response_data['image'] = user.image

    return response_data

def markSearchName(request):
    query = request.GET['query']
    cursor = connection.cursor()
    user = None
    try:
        # search ny email
        user = user_login(query)#User.objects.get(email=query)
        #return HttpResponseRedirect('/%d' % int(user.id))
    except:
        pass
    if user is None:
        try:
            # search by name
            #user = User.objects.get(name__iexact=query)
            user = user_by_name(query)#User.objects.get(email=query)
            #return HttpResponseRedirect('/%d' % int(user.id))
        except:
            pass

    response_data = {}
    if user is not None:
        response_data['id'] = user.id
        response_data['name'] = user.name
        response_data['password'] = user.password
        response_data['email'] = user.email
        response_data['last_update'] = user.last_update
        response_data['score'] = user.score
        response_data['image'] = user.image
    else:
        response_data['id'] = -1
        response_data['name'] = ''
        response_data['password'] = ''
        response_data['email'] = ''
        response_data['last_update'] = 0
        response_data['score'] = 0
        response_data['image'] = ''

    return HttpResponse(json.dumps(response_data), content_type='application/json')

# get should include session
def markScoreboard(request):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users ORDER BY score DESC LIMIT 10")
    users = cursor.fetchall()
    temp = []
    for user in users:
        temp.append(get_user_from_tuple(user))
    users = temp

    user = None
    if 'user_email' in request.session:
        user = user_login(request.session['user_email'])
    
    response_data = {}
    response_data['user'] = unpack_user(user)
    arr = []
    for u in users:
        arr.append(unpack_user(u))

    response_data['users'] = arr
    #return render(request, 'index.html', {'request':request, 'users':users, 'user':user})
    return HttpResponse(json.dumps(response_data), content_type='application/json')

def markVote(request):
    voter = '';
    try:
        voter = request.session['user_email']
    except:
        score = 'notLoggedIn'
        response_data = {}
        response_data['score'] = score
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    votee = request.POST['email']

    db=get_db()
    cursor = db.cursor()#connection.cursor()
    #score = cursor.execute("SELECT score FROM hello_User WHERE email = '%s'" % votee).fetchone()[0]
    cursor.execute("SELECT score FROM Users WHERE email = '%s'" % votee)
    score = cursor.fetchone()[0]
    if votee != voter:
        cursor.execute("""SELECT last_update 
                                        FROM Votes 
                                        WHERE voter = '%s' AND votee = '%s'"""
                                        % (voter, votee)
                                    )
        canVote = True
        epoch = int(time.time())
        last_tuple = cursor.fetchone()
        if last_tuple is None:
            vote_create(voter, votee, epoch, 1)
        elif last_tuple[0] is not None:
            last = last_tuple[0]
            canVote = epoch - last > 60
            if not canVote:
                score = 'tooQuick'
        else:
            canVote = False
            score = 'noneError'
        if canVote:
            change = 1 if (request.POST['direction'] == 'upvote') else -1
            score += change
            cursor.execute("UPDATE Users SET score = %d WHERE email = '%s'" % (score, votee))
            cursor.execute("""UPDATE Votes 
                              SET last_update = %d 
                              WHERE voter = '%s' 
                              AND votee = '%s'"""
                            % (epoch, voter, votee)
                        )
    else:
        score = 'self'
    db.commit()
    db.close()
    response_data = {}
    response_data['score'] = 'valid'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def markLogin(request):
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
        pw = get_hashed_password(request.POST['password'])

        try:
            user = user_login(email) #User.objects.get(email=email);
        except:
            user = None

        if user and pw == user.password:
            request.session['user_email'] = email
            return HttpResponseRedirect('/account')

        params['emailInput'] = email
        params['emailError'] = 'Invalid username or password'
        params['passwordError'] = ''
        return render(request, 'login.html', params)

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
        pw = get_hashed_password(request.POST['password'])

        try:
            user = user_login(email) #User.objects.get(email=email);
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
        try:
            image = request.FILES['image']
        except:
            pass

        nameError, verifyError, emailError = validate(name, pw1, pw2, email)
        if nameError + verifyError + emailError == '':
            user_register(name, pw1, email, image)
            return HttpResponseRedirect('/login')
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
        #params['user'] = User.objects.get(email=request.session['user_email'])
        email = request.session['user_email']
        params['user'] = user_login(email)
        params['users'] = join_query(email)
        return render(request, 'account.html', params)
    else:
        return HttpResponseRedirect('/login')
    
def add(request):
    params = { 'user': None, 'request' : request }
    if 'user_email' in request.session:
        #params['user'] = User.objects.get(email=request.session['user_email'])
        email = request.session['user_email']
        params['user'] = user_login(email)
        return render(request, 'add.html', params)
    else:
        return HttpResponseRedirect('/login')

def profile(request, userid):
    params = { 'user': None, 'request' : request }
    if 'user_email' in request.session:
        #params['user'] = User.objects.get(email=request.session['user_email'])
        email = request.session['user_email']
        params['user'] = user_login(email)

    try:
        #params['person'] = User.objects.get(id=userid)
        params['person'] = user_by_id(userid)
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
    '''
    #user = User.objects.get(email = email)
    try:
        pass#os.remove(BASE_DIR + '/../mediafiles/'+user.imgurl)
    except:
        pass
    '''

    user_delete(email)
    #cursor = connection.cursor()
    #cursor.execute("DELETE FROM hello_User WHERE email = '%s'" % email)
    return HttpResponseRedirect('/login')

def reverse(request):
    email = 'error'
    try:
        email = request.session['user_email']
    except KeyError:
        pass
    user = user_login(email)
    db=get_db()
    db.cursor().execute("UPDATE Users SET name = '%s' WHERE id = %d" % (user.name[::-1], int(user.id)))
    db.commit()
    db.close()
    return HttpResponseRedirect('/account')

def vote(request):
    voter = '';
    try:
        voter = request.session['user_email']
    except:
        score = 'notLoggedIn'
        response_data = {}
        response_data['score'] = score
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    votee = request.POST['email']

    db=get_db()
    cursor = db.cursor()#connection.cursor()
    #score = cursor.execute("SELECT score FROM hello_User WHERE email = '%s'" % votee).fetchone()[0]
    cursor.execute("SELECT score FROM Users WHERE email = '%s'" % votee)
    score = cursor.fetchone()[0]
    if votee != voter:
        cursor.execute("""SELECT last_update 
                                        FROM Votes 
                                        WHERE voter = '%s' AND votee = '%s'"""
                                        % (voter, votee)
                                    )
        canVote = True
        epoch = int(time.time())
        last_tuple = cursor.fetchone()
        if last_tuple is None:
            vote_create(voter, votee, epoch, 1)
        elif last_tuple[0] is not None:
            last = last_tuple[0]
            canVote = epoch - last > 60
            if not canVote:
                score = 'tooQuick'
        else:
            canVote = False
            score = 'noneError'
        if canVote:
            change = 1 if (request.POST['direction'] == 'upvote') else -1
            score += change
            cursor.execute("UPDATE Users SET score = %d WHERE email = '%s'" % (score, votee))
            cursor.execute("""UPDATE Votes 
                              SET last_update = %d 
                              WHERE voter = '%s' 
                              AND votee = '%s'"""
                            % (epoch, voter, votee)
                        )
    else:
        score = 'self'
    db.commit()
    db.close()
    response_data = {}
    response_data['score'] = score
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def db(request):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    return render(request, 'db.html', {'request':request,'users':users})

def images(request, user_id, file_ext):
    return get_image(user_id, file_ext)

# advanced feature: recommendations

"""
def get_next_state(links, cur_state):
    result = np.zeros(len(cur_state))
    for link, amount in zip(links, cur_state):
        for dest in link:
            result[dest] += amount / float(len(link))
    return result

s_p = initial_state
first_state = get_next_state(links, s_p)
while True:
    s_n = get_next_state(links, s_p)
    if max(abs(s_n - s_p)) < 1e-9: # TODO: also limit on number of iterations
        break
    s_p = s_n
    """

def recommended(request):
    if 'user_email' not in request.session:
        return HttpResponseRedirect('/account')

    cur_user = request.session['user_email']

    scores = {}
    scores[cur_user] = -1

    # get data
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT votee FROM Votes WHERE voter = '%s'" % (cur_user, ))
    votees = cursor.fetchall()
    for votee_tuple in votees:
        scores[votee_tuple[0]] = -1
        cursor.execute("SELECT votee FROM Votes WHERE voter = '%s'" % (votee_tuple[0], ))
        sub_votees = cursor.fetchall()
        for sub_votee in sub_votees:
            sub_name = sub_votee[0]
            if sub_name not in scores:
                scores[sub_name] = 0
            if scores[sub_name] != -1:
                scores[sub_name] += 1 / len(sub_votees)

    import operator
    sorted_x = sorted(scores.items(), reverse=True, key=operator.itemgetter(1))
    sorted_x = sorted_x[:9]


    result_x = []
    for i in sorted_x:
        if i[1] != -1:
            result_x.append(i)
    sorted_x = result_x

    # find recommendations
    temp = []
    for x in sorted_x:
        cursor.execute("SELECT * FROM Users WHERE email = '%s'" % (x[0], ))
        user = cursor.fetchall()
        temp.append(get_user_from_tuple(user[0]))
    users = temp

    # put into state

    return render(request, 'recommendations.html', {'request':request, 'users':users, 'user':cur_user})

