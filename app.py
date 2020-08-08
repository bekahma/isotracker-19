# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime
from dateutil import relativedelta
import random

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='something',
                       db='something',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#============== app =================
@app.route('/')
def public():
    loggedin=None
    if session != {}:
        loggedin=True
    return render_template('index.html', loggedin=loggedin)

#---------login & authentication-------
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM users WHERE username = %s and password = md5(%s)'
    cursor.execute(query, (username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if (data):
        # creates a session for the the user
        # session is a built in dictionary
        session['username'] = username
        return redirect(url_for('home'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)  # send the error msg to html
