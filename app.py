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
import dbconn2
import json

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
                           
@app.route('/profile')
def index():
  return render_template('profile.html',
                           title='Profiles')

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



