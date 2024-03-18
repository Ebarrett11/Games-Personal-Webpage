# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from flask import send_from_directory
import http.client
import datetime 
from datetime import date
from . import socketio

db = database()

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
# Added to other function, means user must be logged in to access
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

# Returns user's email
def getUser():
	return db.reversibleEncrypt('decrypt',  session['email']) if 'email' in session else 'Unknown'



@app.route('/projects')
def projects():
	return render_template('projects.html', user=getUser())

@app.route('/piano')
def piano():
	return render_template('piano.html', user=getUser())

@app.route('/login')
def login():
  session['instructions'] = True
  return render_template('login.html', user=getUser())

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/create')
def create():  
	return render_template('create.html', user=getUser())

# Takes username and password and sends it to database to create a user
@app.route('/createaccount', methods = ["POST","GET"])
def createaccount():
  form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
  email = form_fields['email']
  password = form_fields['password']
  x = db.createUser(email,password)
  return json.dumps(x)

# Takes  username and password and sends it to database to authenticate a log in
@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
  form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
  email = form_fields['email']
  password = form_fields['password']
  if(db.authenticate(email,password) == {'success' : 1}):
    session['email'] = db.reversibleEncrypt('encrypt', form_fields['email']) 
    return json.dumps({'success':1})
  return json.dumps({'success':0})




  


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

# Called when the user joins the chat
@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')

# Used for handling messages
@socketio.on('message',namespace='/chat')
def handle_message(message):
    emit(message)
    
#######################################################################################
# WORDLE RELATED
#######################################################################################

# Returns false if user has seen instructions
def getInstructions():
  x = session['instructions']
  session['instructions'] = False
  return x

# returns word of the day
def getWord():
  x = db.query("SELECT word FROM wordle")
  y = (x[-1])['word']
  return y.upper()

#for getting information from another website
#https://stackoverflow.com/questions/33473803/how-to-get-json-data-from-another-website-in-flask
@app.route('/wordle')
@login_required
def wordle():
  words = {}
  words_dict = {0: "certain", 1: "refer", 2: "cream", 3: "Bible", 4: "compose", 5: "glare", 6: "laser", 7: "wording", 8: "puzzle", 9: "pocket", 10: "window", 11: "insight", 12: "mile", 13: "safety", 14: "mellow", 15: "popular", 16: "coffee", 17: "rocket", 18: "oral", 19: "moment", 20: "bedroom", 21: "steel", 22: "bluebird", 23: "raindrop", 24: "whistles", 25: "disco", 26: "watering", 27: "mountain", 28: "crop", 29: "wondered", 30: "climbing"}
  today = date.today()
  # https://www.geeksforgeeks.org/comparing-dates-python/
  test_date = datetime.date(2024, 3, 4) 
  dif = (today - test_date)
  word_of_day = words_dict[(dif.days)]

 

  db.setWord(word_of_day) 
  return render_template('wordle.html', user=getUser(), instructions =getInstructions())


# Creates the id's for the tiles 
# creates n^2 id's
@app.route('/renderGame', methods = ["POST","GET"])
def renderGame():
  wordLen = len(getWord())
  boxDict = {}
  for i in range(wordLen):
    for j in range(wordLen):
        x = str(i) + str(j)
        boxDict[x] = (0, '')
  return json.dumps(boxDict)





@app.route('/interpretGuess', methods = ["POST","GET"])
def interpretGuess():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    guess = form_fields['guess']
    turns = int(form_fields['turns'])
    word = getWord()
    word_save = word
    #wordsapi tutorial
    #https://rapidapi.com/dpventures/api/wordsapi
    # Call API

    conn = http.client.HTTPSConnection("wordsapiv1.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': "b4cc972465mshe98d8aec1aec440p148192jsn1cc8cd640110",
        'X-RapidAPI-Host': "wordsapiv1.p.rapidapi.com"
    }
    url = "/words/" + guess + "/definitions"
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    #https://stackoverflow.com/questions/40059654/convert-a-bytes-array-into-json-format
    my_json = data.decode('utf8').replace("'", '"')  
    return_dict = {}
    guessed = True
    return_dict["word"] = word #save secret word
    if(my_json.find("definitions")!= -1):
    # if('definitions' in data_json): #is a word
      return_dict['success'] = 1
      #https://stackoverflow.com/questions/47351334/python-joint-enumerate-with-multiple-variables
      for i, (g,w) in enumerate(zip(guess,word)):
        if(g==w): #guess letter = word letter
          # letter at index replace
          # https://stackoverflow.com/questions/41752946/replacing-a-character-from-a-certain-index
          word = word[:i] + "*" + word[i + 1:]
      for i, (g,w) in enumerate(zip(guess,word)):
          if(w == '*'): #means letter was correct
            return_dict[i] = 2
          elif(g in word): #yellow means letter is correct, just wrong place
            guessed = False
            return_dict[i] = 1
          else: #Gray incorrect letter 
            guessed = False
            return_dict[i] = 0
    else: #isn't a word
      return_dict['success'] = 0
      guessed = False
    if(guessed): #all letters correct
        return_dict['success'] = 2
        db.updateScore(getWord(),getUser(),turns)
    leaderboard = db.getLeaderboard(word_save)
    #set default values for scoreboarrd
    for i in range(5):
      dict_string = "score_" + str(i)
      return_dict[dict_string] = "No Score Entry"
    #if score is available add to leaderboard
    for i, score in enumerate(leaderboard):
      if(i>4):
        break
      dict_string = "score_" + str(i)
      return_dict[dict_string] = str(score[0]) + " || Turns: " + str(score[1])
    return json.dumps(return_dict)
          
    
    

#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	x = random.choice(['I started university when I was a wee lad of 15 years.','I have a pet sparrow.','I write poetry.'])
	return render_template('home.html', user=getUser(), fun_fact = x)

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r