from  __future__  import print_function
import pyrebase
from flask import *
from datetime import datetime
import pickle
import os.path
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

app = Flask(__name__)

config = {
    "apiKey": "AIzaSyDQkaQjhaa0ueRT_D-1vVtXMbX8xtqPwBI",
    "authDomain": "covid-19-isolation-tracker.firebaseapp.com",
    "databaseURL": "https://covid-19-isolation-tracker.firebaseio.com",
    "projectId": "covid-19-isolation-tracker",
    "storageBucket": "covid-19-isolation-tracker.appspot.com",
    "messagingSenderId": "435855688991",
    "appId": "1:435855688991:web:17bcb9b15f945d4cc11c2a",
    "measurementId": "G-JBSNN6Z8DV"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
db = firebase.database()

def noquote(s):
    return s
pyrebase.pyrebase.quote = noquote

def getPastData(uid, days):
    pastData = []
    for day in range(14):
        if day <= days:
            oneDay = db.child("users").child(uid).child(14 - day).get().val()
            rate = 0
            for key in oneDay.keys():
                if key == 'temperature':
                    if float(oneDay[key]) >= 37.3:
                        rate = 1
                        break
                elif key != 'date':
                    if oneDay[key] == 1:
                        rate = 1
                        break
            pastData.append(rate)
        else:
            pastData.append(None)
    return pastData

@app.route('/', methods = ['GET', 'POST'])
def public():
    loggedin=None
    if session != {}:
        loggedin=True
        uid = session['uid']
        generalData = db.child("users").child(uid).get().val()
        startDate = datetime.strptime(generalData["startDate"], '%Y-%m-%d-%H:%M:%S')
        today = datetime.now()
        days = abs((today - startDate).days)
        daysLeft = 14 - days
        today = today.strftime('%Y-%m-%d')
        if daysLeft <= 0:
            daysLeft = 0
            data = "Congratulations! You've finished your 14-day quarantine!"
            pastData = []
        else:
            #get old data
            pastData = getPastData(uid, days)
            data = db.child("users").child(uid).child(daysLeft).get().val()
            if not data:
                data = db.child("users").child(uid).child(daysLeft+1).get().val()
        return render_template("tracker.html", pastData=pastData, data=data, daysLeft=daysLeft, today=today)
    return render_template('index.html', loggedin=loggedin)

#--------------register
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registration', methods=['GET', 'POST'])
def enter_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['Pass']
        try:
            #create new user
            user = auth.create_user_with_email_and_password(email, password)
            uid = user['localId']
            today = datetime.now()
            today = today.strftime("%Y-%m-%d-%H:%M:%S")
            # today = '2020-06-20-00:00:00'
            #set up db item for user with key=uid
            data = {
                "email": email,
                "startDate": today
            }
            db.child("users").child(uid).set(data)
            moreData = {
                "date": today,
                "temperature": 0.0,
                "breath": 0,
                "cough": 0,
                "fatigue": 0,
                "bodyache": 0,
                "headache": 0,
                "taste": 0,
                "throat": 0,
                "nose":0,
                "nausea":0,
                "diarrhea":0
            }
            db.child("users").child(uid).child(14).set(moreData)
            return render_template('index_login.html')
        except:
            return render_template('register.html')


#--------login
@app.route('/login')
def login():
    return render_template('index_login.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['Pass']
        try:
            #user sign in
            user = auth.sign_in_with_email_and_password(email,password)
            #get user data from db
            uid = user['localId']
            #save session
            session['uid'] = uid
            #get days
            generalData = db.child("users").child(uid).get().val()
            startDate = datetime.strptime(generalData["startDate"], '%Y-%m-%d-%H:%M:%S')
            today = datetime.now()
            days = abs((today - startDate).days)
            daysLeft = 14 - days
            today = today.strftime('%Y-%m-%d')
            if daysLeft <= 0:
                daysLeft = 0
                data = "Congratulations! You've finished your 14-day quarantine!"
                pastData = []
            else:
                #get old data
                pastData = getPastData(uid, days)
                data = db.child("users").child(uid).child(daysLeft).get().val()
                if not data:
                    data = db.child("users").child(uid).child(daysLeft+1).get().val()
            return render_template("tracker.html", pastData=pastData, data=data, daysLeft=daysLeft, today=today)
        except:
            return render_template('index_login.html')


#-----------------tracker update
@app.route('/checklist', methods=['GET','POST'])
def checklist():
    if request.method == 'POST' and session.get('uid'):
        temperature = request.form['temperature']
        breath = request.form.get('breath', 0)
        cough = request.form.get('cough', 0)
        fatigue = request.form.get('fatigue', 0)
        bodyache = request.form.get('bodyache', 0)
        headache = request.form.get('headache', 0)
        taste = request.form.get('taste', 0)
        throat = request.form.get('throat', 0)
        nose = request.form.get('nose', 0)
        nausea = request.form.get('nausea', 0)
        diarrhea = request.form.get('diarrhea', 0)
        try:
            uid = session['uid']
            #get days
            generalData = db.child("users").child(uid).get().val()
            startDate = datetime.strptime(generalData["startDate"], '%Y-%m-%d-%H:%M:%S')
            today = datetime.now()
            days = abs((today - startDate).days)
            daysLeft = 14 - days
            today = today.strftime('%Y-%m-%d')
            pastData = []
            #get old data
            pastData = getPastData(uid, days)
            #get new data
            newData = {
                "date": today,
                "temperature": temperature,
                "breath": breath,
                "cough": cough,
                "fatigue": fatigue,
                "bodyache": bodyache,
                "headache": headache,
                "taste": taste,
                "throat": throat,
                "nose":nose,
                "nausea":nausea,
                "diarrhea":diarrhea
            }
            if db.child("users").child(uid).child(daysLeft).get():
                db.child("users").child(uid).child(daysLeft).update(newData)
            else:
                db.child("users").child(uid).child(daysLeft).set(newData)
            return render_template("tracker.html", pastData=pastData, data=newData, daysLeft=daysLeft, today=today)
        except:
            return render_template("tracker.html", data="error", daysLeft="error", today="error")


#------post about quarantine
@app.route('/addPost', methods=['GET', 'POST'] )
def addPost():
    username = request.form['username']
    blogPost = request.form['blogPost']
    if request.method == 'POST' and session.get('uid'):
        uid = session['uid']
        timestamp = int(datetime.now().timestamp())
        data = {
            "uid": uid,
            "username": username,
            "blogPost": blogPost
        }
        db.child("posts").child(timestamp).set(data)
        results = db.child("posts").order_by_key().limit_to_last(10).get()
        posts = []
        for item in results.each():
            posts.append(item.val())
        return render_template("posts.html", posts=posts)


#------post about quarantine
@app.route('/getPost', methods=['GET', 'POST'] )
def getPost():
    if session.get('uid'):
        results = db.child("posts").order_by_key().limit_to_last(10).get()
        posts = []
        for item in results.each():
            posts.append(item.val())
        return render_template("posts.html", posts=posts)


@app.route('/logout', methods=['GET','POST'])
def logout():
    #logout the user
    session.pop("uid", None)
    return render_template('index.html')


#secret key
app.secret_key = b'_5askq478eqrbkhdfs]/'

if __name__ =='__main__':
    app.run(debug=True)
