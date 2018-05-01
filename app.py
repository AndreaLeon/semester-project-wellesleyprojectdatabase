# Andrea Leon, Eliana Marostica, and Parul Kohl
# CS304 Final Project: Wellesley Project Database
# app.py 
# created 4/28/2018
#!/usr/local/bin/python2.7

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug import secure_filename
app = Flask(__name__)

import sys,os,random
import bcrypt
import dbconn2
import json
import updateDB

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
  return render_template('main.html',
                           title='Main Page')


@app.route('/join/', methods=["POST"])
def join():
    try:
#TODO: what if user doesn't input name, etc? What if name has numbers? ###################################
        name = request.form['name']
        email = request.form['email']
        passwd1 = request.form['passwd1']
        passwd2 = request.form['passwd2']
        rolelist = request.form.getlist('role')
        role = ','.join(rolelist)
        if passwd1 != passwd2:
            flash('Passwords do not match')
            return redirect(url_for('login'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        conn = dbconn2.connect(dsn)

        #check whether account already exists with that email
        row = updateDB.checkUser(conn, email)
        if row is not None:
            flash('An account with that email already exists')
            return redirect( url_for('login') )
        
        #insert new user into user table
        updateDB.addUser(conn, email, name, role, hashed)

        #TO DO: sessions ###########################################################################################
        # session['username'] = username
        # session['logged_in'] = True
        # session['visits'] = 1
        # return redirect( url_for('user', username=username) )
        flash('inserted email')
        return redirect(url_for('index')) #need to change once session are incorporated ###################################
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )



#login 
#Question for Scott: getting error "form submission error coercing to Unicode: need string or buffer, long found" ????????????????????????????????????????????????????????????????/
  #tried casting both passwd and hashed to str because they are the only values being encoded, but still got same error
@app.route('/login/', methods=['GET','POST'])
def login():
  conn = dbconn2.connect(dsn)
  if request.method == 'GET':
    return render_template('login.html')
  else:
    try:
        email = request.form['email']
        passwd = request.form['passwd']
        print('passwd: ' + passwd, passwd.encode('utf-8'))
        conn = dbconn2.connect(dsn)
        row = updateDB.fetchHashed(conn, email)
        if row is None:
            # Same response as wrong password, so no information about what went wrong
            flash('Login incorrect. Try again or join.')
            return redirect( url_for('login'))
        hashed = row['hashed']
        print('hashed: ' + hashed,hashed.encode('utf-8'))

        print bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))
        if bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
            uid = updateDB.getUID(conn, email)
            name = updateDB.getName(conn, email)

            flash(('Successfully logged in as {}, user number {}, with email {}').format(name,uid,email))
            session['uid'] = uid
            session['logged_in'] = True
            session['name'] = name
            # session['visits'] = 1 ------------> keep track of number of visits???????
            return redirect( url_for('user', uid=uid) )
        
        else:
            flash('Login incorrect. Try again or join')
            return redirect( url_for('login'))

    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

#user
@app.route('/user/<uid>')
def user(uid):
    try:
        # don't trust the URL; it's only there for decoration
        if 'uid' in session:
            uid = session['uid']
            name = session['name']
            # session['visits'] = 1+int(session['visits']) ------------> keep track of number of visits???????
            return render_template('greet.html',
                                   page_title='My App: Welcome '+ name,
                                   name= name#,
                                   #visits=session['visits'] ------------> keep track of number of visits???????
                                   )

        else:
            flash('You are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )
                           
# @app.route('/profile')
# def index():
#   return render_template('profile.html',
#                            title='Profiles')

if __name__ == '__main__':

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    dsn = dbconn2.read_cnf()
    dsn['db'] = 'wprojdb_db'
    app.debug = True
    app.run('0.0.0.0',port)



