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


# @app.route('/join/', methods=["POST"])
# def join():
#     try:
#         email = request.form['email']
#         passwd1 = request.form['passwd1']
#         passwd2 = request.form['passwd2']
#         if passwd1 != passwd2:
#             flash('Passwords do not match')
#             return redirect(url_for('login'))
#         hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
#         row = updateDB.addUser(conn, email, hashed)
#         if row is not None:
#             flash('That username is taken')
#             return redirect( url_for('index') )
#         curs.execute('INSERT into userpass(username,hashed) VALUES(%s,%s)',
#                      [username, hashed])
#         session['username'] = username
#         session['logged_in'] = True
#         session['visits'] = 1
#         return redirect( url_for('user', username=username) )
#     except Exception as err:
#         flash('form submission error '+str(err))
#         return redirect( url_for('index') )


#login 
@app.route('/login/', methods=['GET','POST'])
def login():
  conn = dbconn2.connect(DSN)
  if request.method == 'GET':
    return render_template('login.html')
  else:
    try:
      email = request.form['login_email']
      password = request.form['login_passwd']
      flash('Login Succeded')
    except Exception as e:
      flash('Not a Login Attempt')

    try:
      email = request.form['join_email']
      password1 = request.form['join_passwd1']
      password2 = request.form['join_passwd2']
      flash('Join Succeded')
    except Exception as e:
      flash('Not a Join Attempt')

    
    # #check that login hasn't been formed yet
    # if staffExists is not None and password == 'secret':
    #   resp = make_response(redirect(url_for('login')))
    #   resp.set_cookie('uid', username)                                        
    #   flash('Login Succeeded')
    #   return resp
    # else:
    #   flash('Login Failed. Please try again.')
      
    return redirect(url_for('login'))

                           
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
    DSN = dbconn2.read_cnf()
    DSN['db'] = 'wprojdb_db'
    app.debug = True
    app.run('0.0.0.0',port)



