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

app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
  return render_template('main.html',
                           title='Main Page')


@app.route('/join/', methods=["POST"])
def join():
    try:
        name = request.form['name']
        email = request.form['email']
        passwd1 = request.form['passwd1']
        passwd2 = request.form['passwd2']
        rolelist = request.form.getlist('role')
        role = ','.join(rolelist)

        #check that each field has been filled out
        if not name or not email or not passwd1 or not passwd2 or not rolelist:
          flash('Please make sure each field has been filled.')
          return redirect(url_for('login'))

        #check that passwords match
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
        uid = updateDB.getUIDName(conn, email)[0]

        session['uid'] = uid
        session['logged_in'] = True
        session['name'] = name

        flash(('Successfully joined as {}, user number {}, with email {}').format(name,uid,email))
        
        return redirect( url_for('user', uid=uid) ) # ???????????????????????? how do I incorporate cookies into a redirect??????????????????

    except Exception as err:
        flash('Form submission error '+str(err))
        return redirect( url_for('index') )



#login 
@app.route('/login/', methods=['GET','POST'])
def login():
  conn = dbconn2.connect(dsn)
  flaskuid = request.cookies.get('flaskuid')
  
  if not flaskuid:
    print('no cookie set')
    if request.method == 'GET':
      #case 1: first visit, just render form
      return render_template('login.html', allCookies=request.cookies)
    else:
      #case 2: user submitted a form with their name ???????????? Other question: how to recognize whether its a student that's logged in or administrator or what? How to show certain links only to certain people (such as administrators vs students who want to approve/browse projects)?????????
      try:
        email = request.form['email']
        passwd = request.form['passwd']
        row = updateDB.fetchHashed(conn, email)
        if row is None:
            # Same response as wrong password, so no information about what went wrong
            flash('Login incorrect. Try again or join.')
            return redirect( url_for('login'))
        hashed = row['hashed']

        if bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
            uid = updateDB.getUIDName(conn, email)[0]
            name = updateDB.getUIDName(conn, email)[1]

            session['uid'] = uid
            session['logged_in'] = True
            session['name'] = name

            resp = make_response(redirect( url_for('user', uid=uid) ))
            resp.set_cookie('flaskuid', str(uid))
            resp.set_cookie('flaskname', name)

            flash(('Successfully logged in as {}, user number {}, with email {}').format(name,uid,email))

            return resp
        
        else:
            flash('Login incorrect. Try again or join')
            return redirect( url_for('login'))

      except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )
  else:
    print "cookie is set, so either they are continuing or logging out"
    #case 3: just a regular visit, show the user's info
    return redirect(url_for('user', uid=request.cookies.get('flaskuid')))
          

#user
@app.route('/user/<uid>')
def user(uid):
  try:
      if 'uid' in session:
        uid = session['uid']
        name = session['name']
        return render_template('greet.html',
                                name= name,
                                allCookies=request.cookies
                               )
      elif request.cookies.get('flaskuid'):
        return render_template('greet.html',
                                name= request.cookies.get('flaskname'),
                                allCookies=request.cookies
                               )

      else:
          flash('You are not logged in. Please login or join')
          return redirect( url_for('index') )
  except Exception as err:
      flash('some kind of error '+str(err))
      return redirect( url_for('index') )
                           
@app.route('/logout/')
def logout():
#case 4: user wants to delete the cookies, i.e. logout
  try:
    if request.cookies.get('flaskuid'):
      if 'uid' in session:
        username = session['uid']
        session.pop('uid')
        session.pop('name')
        session.pop('logged_in')

      resp = make_response(redirect(url_for('index')))
      resp.set_cookie('flaskuid','',expires=0)
      resp.set_cookie('flaskname','',expires=0)

      flash('You are logged out. Thank you for visiting!')
      return resp
    else:
      flash('You are not logged in. Please login or join')
      return redirect( url_for('index') )
  except Exception as err:
    flash('some kind of error '+str(err))
    return redirect( url_for('index') )


@app.route('/createProfile',  methods=['GET', 'POST'])
def createProfile():
  conn = dbconn2.connect(dsn)
  if request.method == 'POST':
    try: 
      if 'uid' in session:
        uid = session['uid']
        major = request.form['major']
        prog_languages = request.form['prog_languages']
        courses = request.form['courses']
        research_exp = request.form['research_exp']
        internship_exp = request.form['internship_exp']
        bg_info = request.form['bg_info']
        updateDB.updateUser(conn, major, prog_languages, courses, research_exp, 
        internship_exp, bg_info, uid)
        flash ("Profile Update Submitted")
      else:
        flash("You have to be logged in to access this page.")
    except Exception as e:
      flash(e)
      flash('Incorrectly filled, try again')
  return render_template('profile.html')


@app.route('/createProject', methods=['GET', 'POST'])
def createProject():
  conn = dbconn2.connect(dsn)
  if request.method == 'POST':
    try: 
      projName = request.form['projectTitle']
      projDur = request.form['duration']
      projComp = request.form['compensation']
      projRoles = request.form['rolesOpen']
      projReq = request.form['requirements']
      projDesc = request.form['description']
      projCreator = 1 #hard coded until can get user info (to do in Alpha)
      if (projName == '' or projDur == '' or projComp == '' or projRoles == ''\
        or projReq == '' or projDesc == ''):
        flash('Please fill out all fields.')
      else:
        updateDB.addProject(conn, projCreator, projName, projDur, projComp,\
         projRoles, projReq, projDesc)
        flash ("Project Submitted")
    except Exception as e:
      flash('Incorrectly filled, try again')
  return render_template('project.html')


@app.route('/projectApproval', methods=['POST', 'GET'])
def projectApproval():
  conn = dbconn2.connect(dsn)
  try:
    if 'uid' in session:
      uid = session['uid']
      roleDB = updateDB.checkUserRole(conn, uid)
      if roleDB['role']:
        if request.method == 'POST':
          flash('in post')
          selectedPIDs = request.POST.getlist('projectID')
          for pid in selectedPIDs:
            flash(pid)
            updateDB.approveProject(conn, uid, pid) 
            flash("selection approved")
        else:
          projects = updateDB.getUnapprovedProjects(conn)
          return render_template('projectApproval.html',
                                projects = projects
                               )
      else:
        flash('Only administrators have access to this page, please login with an admin account')
    else:
        flash('You are not logged in. Please login or join')
        return redirect( url_for('index') )
  except Exception as e:
    flash(e)
    return redirect( url_for('index') )



@app.route('/browseProjects/', methods=['GET', 'POST'])
def browseProjects():
  conn = dbconn2.connect(dsn)
  try:
    if 'uid' in session:
      uid = session['uid']
      roleDB = updateDB.checkUserRole(conn, uid)
      if 'student' in roleDB['role']:
        if request.method == 'POST':
          # flash('in post')
          # selectedPIDs = request.POST.getlist('projectID')
          # for pid in selectedPIDs:
          #   flash(pid)
          #   # updateDB.approveProject(conn, uid, pid) 
          #   updateDB.applyToProject(conn, uid, pid)
          #   flash("selection approved")
          # # pass
          pid = request.form['projectID']
          result = updateDB.applyToProject(conn, uid, pid)
          if result == None:
            flash('You have already applied to project ' + pid + '. You cannot apply to a project twice. ')
          else:
            flash('You have successfully applied to project  number ' + pid)
          projects = updateDB.getProjects(conn)
        else:
          projects = updateDB.getProjects(conn)
        return render_template('browse.html',
                              projects = projects
                              )
      else:
        flash('Only students have access to this page, please login with a student account')
    else:
        flash('You are not logged in. Please login or join')
  except Exception as e:
    flash(e)
  return redirect( url_for('index') )


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
