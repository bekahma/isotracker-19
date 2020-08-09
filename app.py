from  __future__  import print_function
import pyrebase
from flask import *
import datetime
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

@app.route('/', methods = ['GET', 'POST'])
def public():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    if request.method == 'POST':
        email = request.form['name']
        password = request.form['pass']
        try:
            auth.sign_in_with_email_and_password('email','password')
            return 'Login is successful'
        except:
            error = 'Invalid login or username'
            return render_template('login.html', error=error)

@app.route('/dashboard')
def cal():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with  open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            # with open('token.pickle', 'wb') as token: # can't write files in Google App Engine so comment out or delete
            # pickle.dump(creds, token)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() +  'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='find your cal id from google and paste it here', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    # for event in events:
    # start = event['start'].get('dateTime', event['start'].get('date'))
    # print(start, event['summary'])
    event_list = [event["summary"] for event in events]
    
    return render_template('dashboard.html', events = events_list)



if __name__ =='__main__':
    app.run(debug=True)
