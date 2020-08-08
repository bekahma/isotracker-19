import pyrebase
from flask import *

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



#email = input('Please enter your email\n')
#password = input('Please enter your password\n')

#user = auth.create_user_with_email_and_password(email, password)

#user = auth.sign_in_with_email_and_password(email, password)

#auth.get_account_info(user['idToken'])

if __name__ =='__main__':
    app.run(debug=True)
