# Andrea Leon, Eliana Marostica, and Parul Koul
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
  conn = dbconn2.connect(dsn)
  roleCheck = updateDB.getRole(conn, session)
  return render_template('main.html',
                           title='Main Page',
                           role = roleCheck)

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
        
        return redirect( url_for('user', uid=uid) )

    except Exception as err:
        flash('Form submission error '+str(err))
        return redirect( url_for('index') )



#login 
@app.route('/login/', methods=['GET','POST'])
def login():
  conn = dbconn2.connect(dsn)
  flaskemail = request.cookies.get('flaskemail')
  roleCheck = updateDB.getRole(conn, session)
  if request.method == 'GET':
    if 'uid' in session:
      return redirect(url_for('user', uid=session['uid']))
    else:
      return render_template('login.html',
                              email=flaskemail if flaskemail else "",
                              allCookies=request.cookies, 
                              role = roleCheck)
  else:
    #case 2: user submitted a form with their name 
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
          resp.set_cookie('flaskemail', email)

          flash(('Successfully logged in as {}, user number {}, with email {}').format(name,uid,email))

          return resp
      
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
      conn = dbconn2.connect(dsn)
      roleCheck = updateDB.getRole(conn, session)
      if 'uid' in session:
        uid = session['uid']
        name = session['name']
        return render_template('greet.html',
                                name=name,
                                allCookies=request.cookies,
                                role = roleCheck
                               )
      else:
          flash('You are not logged in. Please login or join')
          return redirect( url_for('login') )
  except Exception as err:
      flash('some kind of error '+str(err))
      return redirect( url_for('index') )


                           
@app.route('/logout/')
def logout():
  try:
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
  try: 
    roleCheck = updateDB.getRole(conn, session)
    if 'uid' in session:
      uid = session['uid']
      roleDB = updateDB.checkUserRole(conn, uid)
      if 'student' in roleDB['role']: 
        if request.method == 'POST':
          major = request.form['major']
          prog_languages = request.form['prog_languages']
          courses = request.form['courses']
          research_exp = request.form['research_exp']
          internship_exp = request.form['internship_exp']
          bg_info = request.form['bg_info']
          updateDB.updateUser(conn, major, prog_languages, courses, research_exp, 
          internship_exp, bg_info, uid)
          flash ("Profile Update Submitted")
          return render_template('profile.html', role = roleCheck)
        else:
          return render_template('profile.html', role = roleCheck)
      else:
          flash('Only students have access to this page, please login with a student account')
          return redirect( url_for('index') )
    else:
      flash('You are not logged in. Please login or join')
      return redirect( url_for('index') )
  except Exception as e:
    flash(e)
    flash('Incorrectly filled, try again')
    return redirect( url_for('index') )

# route for createProject
# client type users can create a project to be added to the project DB
@app.route('/createProject', methods=['GET', 'POST'])
def createProject():
  conn = dbconn2.connect(dsn)
  try:
    roleCheck = updateDB.getRole(conn, session)
    if 'uid' in session:
      uid = session['uid']
      roleDB = updateDB.checkUserRole(conn, uid)
      if 'client' in roleDB['role']: 
        if request.method == 'POST':
          projName = request.form['projectTitle']
          projDur = request.form['duration']
          projComp = request.form['compensation']
          projRoles = request.form['rolesOpen']
          projReq = request.form['requirements']
          projDesc = request.form['description']
          projCreator = uid
          if (projName == '' or projDur == '' or projComp == '' or projRoles == ''\
            or projReq == '' or projDesc == ''):
            flash('Please fill out all fields.')
          else:
            updateDB.addProject(conn, projCreator, projName, projDur, projComp,\
            projRoles, projReq, projDesc)
            flash ("Project Submitted")
            return render_template('project.html', role = roleCheck)
        else:
          return render_template('project.html', role = roleCheck) 
      else:
        flash('Only clients have access to this page, please login with a client account')
        return redirect( url_for('index') )
    else:
      flash('You are not logged in. Please login or join')
      return redirect( url_for('index') )
  except Exception as e:
    flash(e)
    return redirect( url_for('index') )

# route for projectApproval
# admin type accounts can approve a client's project to be viewable by student type accounts
@app.route('/projectApproval', methods=['POST', 'GET'])
def projectApproval():
  conn = dbconn2.connect(dsn)
  roleCheck = updateDB.getRole(conn, session)
  try:
    if 'uid' in session:
      uid = session['uid']
      roleDB = updateDB.checkUserRole(conn, uid)
      if 'admin' in roleDB['role']:
        if request.method == 'POST':
          pid = request.form['projectID']
          updateDB.approveProject(conn, uid, pid) 
          flash("selection approved")
        projects = updateDB.getUnapprovedProjects(conn)
        return render_template('projectApproval.html',
                              projects = projects,
                              role = roleCheck
                             )
      else:
        flash('Only administrators have access to this page, please login with an admin account')
        return redirect( url_for('index') )
    else:
        flash('You are not logged in. Please login or join')
        return redirect( url_for('index') )
  except Exception as e:
    flash(e)
    return redirect( url_for('index') )

# route for projectApprovalAjax
# ajax funcitonality allows projects to be approved and remain on page until reload
@app.route('/projectApprovalAjax/', methods=['POST'])
def projectApprovalAjax():
  conn = dbconn2.connect(dsn)

  if 'uid' in session:
    uid = session['uid']
    pid = request.form['pid']
    updateDB.approveProject(conn, uid, pid) 
    return jsonify({'approval':'approved!'})


@app.route('/browseProjects/', methods=['GET', 'POST'])
def browseProjects():
  conn = dbconn2.connect(dsn)
  try:
    if 'uid' in session:
      uid = session['uid']
      roleDB = updateDB.checkUserRole(conn, uid)
      roleCheck = updateDB.getRole(conn, session)
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
                              projects = projects,
                              role = roleCheck
                              )
      else:
        flash('Only students have access to this page, please login with a student account')
    else:
        flash('You are not logged in. Please login or join')
  except Exception as e:
    flash(e)
  return redirect( url_for('index') )

@app.route('/viewApplications/', methods=['GET', 'POST'])
def viewApplications():
  conn = dbconn2.connect(dsn)
  try:
    roleCheck = updateDB.getRole(conn, session)
    if 'uid' in session:
      uid = session['uid']
      roleDB = updateDB.checkUserRole(conn, uid)
      if 'client' in roleDB['role']:
        applications = updateDB.getApplicationsPerClient(conn, uid)
        print(applications)
        return render_template('viewApplications.html', applications=applications, role = roleCheck)
      else:
        flash('Only clients have access to this page, please login with a client account')
    else:
        flash('You are not logged in. Please login or join')
  except Exception as e:
    flash(e)
  return redirect( url_for('index') )


@app.route('/profile/', methods=['GET','POST'])
def profile():
  conn = dbconn2.connect(dsn)
  try:
    roleCheck = updateDB.getRole(conn, session)
    if 'uid' in session:
      return render_template('viewProfile.html', role = roleCheck)
    else:
      flash('You are not logged in. Please login or join')
      return redirect( url_for('index') )
  except Exception as e:
    flash(e)
  return redirect( url_for('index') )

# @app.route('/viewProfile/', methods=['GET', 'POST'])
# def viewProfile():
#   conn = dbconn2.connect(dsn)
#   try:
#     if 'uid' in session:
#       return render_template('viewProfile')
#     else:
#       flash('You are not logged in. Please login or join')
#       return redirect( url_for('login') )
#   except Exception as e:
#     flash(e)
#     return redirect( url_for('index') )

# route for clientProjects
# client type accounts can view projects they have created to see if they have been approved
# and to delete any of their projects
@app.route('/clientProjects', methods=['POST', 'GET'])
def clientProjects():
  conn = dbconn2.connect(dsn)
  roleCheck = updateDB.getRole(conn, session)
  try:
    if 'uid' in session:
      uid = session['uid']
      roleDB = updateDB.checkUserRole(conn, uid)
      if 'client' in roleDB['role']:
        if request.method == 'POST':
          pid = request.form['projectID']
          updateDB.deleteProject(conn, pid) 
          flash("Project Deleted")
        projects = updateDB.getUserProjects(conn, uid)
        return render_template('clientProjects.html',
                              projects = projects,
                              role = roleCheck
                             )
      else:
        flash('Only clients have access to this page, please login with a client account')
        return redirect( url_for('index') )
    else:
        flash('You are not logged in. Please login or join')
        return redirect( url_for('index') )
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
