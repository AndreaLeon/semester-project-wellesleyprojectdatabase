# Andrea Leon, Eliana Marostica, and Parul Kohl
# CS304 Final Project: Wellesley Project Database
# updateDB.py
# created 4/29/2018
#!/usr/local/bin/python2.7


import sys
import MySQLdb
import dbconn2

# ================================================================
# The functions that do most of the work.  

def checkUser(conn, email):
	'''Finds if user exists in user table based on email
		By: Eliana Marostica'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT email FROM user WHERE email = %s', [email])
	return curs.fetchone()

def checkUserRole(conn, uid):
	'''Finds user role in user table based on uid
		By: Andrea Leon'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT role FROM user WHERE uid = %s', [uid])
	return curs.fetchone()

def addProject(conn, projCreator, projName, projDur, projComp, projRoles, projReq, projDesc):
	'''Adds project to project table
	 	by: Andrea Leon'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor) # results as Dictionaries
	curs.execute('INSERT into project (creator, name, compensation, rolesOpen, requirements, description,\
	 duration) VALUES (%s, %s, %s, %s, %s, %s, %s)', [projCreator, projName, projComp, projRoles, projReq, projDesc, projDur])

def getUnapprovedProjects(conn):
	'''gets all projects in project that have NULL approver
		By: Andrea Leon'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT pid, creator, approver, name, compensation, rolesOpen, requirements, description,\
	 duration FROM project WHERE approver is NULL')
	return curs.fetchall()

def approveProject(conn, uid, pid):
  '''adds UID to approver column of project (initially set to NULL)
      By: Andrea Leon'''
  curs = conn.cursor(MySQLdb.cursors.DictCursor) # results as Dictionaries
  curs.execute('UPDATE project SET approver = %s WHERE pid = %s', [uid, pid])

def deleteProject(conn, pid):
  '''deletes project from project based on given pid
      By: Andrea Leon'''
  curs = conn.cursor(MySQLdb.cursors.DictCursor) # results as Dictionaries
  curs.execute('DELETE FROM project WHERE pid = %s', [pid])

def getUserProjects(conn, uid):
	'''gets all projects under given UID"
		By: Andrea Leon'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT pid, creator, approver, name, compensation, rolesOpen,requirements, description, duration FROM project WHERE creator = %s', [uid])
	return curs.fetchall()

def addUser(conn, email, name, role, hashed):
	'''Adds a user to the user table
		By: Eliana Marostica'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('INSERT into user(email,name,role,hashed) VALUES(%s,%s,%s,%s)', [email, name, role, hashed])

def fetchHashed(conn, email):
	'''Retrieves the password hash for a user based on email
		By: Eliana Marostica'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT hashed FROM user WHERE email = %s', [email])
	return curs.fetchone()

def getUIDName(conn, email):
	'''Returns user's uid from user table based on provided email
		By: Eliana Marostica'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT uid, name FROM user WHERE email = %s', [email])
	row = curs.fetchone()
	return row['uid'], row['name']

def getProjects(conn):
	'''Retrieves all projects in the project table that have been approved
	By: Eliana Marostica'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT pid, creator, approver, name, compensation, rolesOpen,requirements, description, duration FROM project WHERE approver IS NOT NULL;')
	return curs.fetchall()

# def getName(conn, email):
# 	'''Returns user's name from user table based on their email
# 		By: Eliana Marostica'''
# 	curs = conn.cursor(MySQLdb.cursors.DictCursor)
# 	curs.execute('SELECT name FROM user WHERE email = %s', [email])
# 	row = curs.fetchone()
# 	return row['name']

def getRole(conn, session):
  '''checks to see user role if UID is present in the session
    By: Andrea Leon'''
  role1 = ''
  if 'uid' in session:
    uid = session['uid']
    roleDB = checkUserRole(conn, uid)
    role1 = roleDB['role']
  return role1

def updateUser(conn, major, prog_languages, courses, research_exp, internship_exp, bg_info, uid):
	'''Updates the user table to add the information input by the
	user on the profile.html page
		By: Parul Koul'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('UPDATE user SET major = %s, programming_languages = %s, courses = %s, \
	research_experience = %s, internship_experience = %s, background_info = %s WHERE uid = %s;', 
	[major, prog_languages, courses, research_exp, internship_exp, bg_info, uid])

def applyToProject(conn, uid, pid):
	'''Updates the application table with new applications. Each application
	consists of a users uid taken from the session and the pid of the project.
		By: Parul Koul'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT * FROM application WHERE uid=%s AND pid=%s;', [uid, pid])
	result = curs.fetchall()
	if len(result) == 0:
		curs.execute('INSERT INTO application (uid, pid) VALUES (%s, %s);', [uid, pid])
		return pid
	else:
		return None

def getApplicationsPerClient(conn, uid):
	'''Gets all the applications associated with all projects associated with a
	particular client
		By: Parul Koul '''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT application.uid, application.pid, project.creator FROM \
	(application INNER JOIN project ON application.pid = project.pid) WHERE project.creator = %s;', [uid])
	applications = curs.fetchall()
	return applications	

def getProfileInfo(conn, uid):
	''' Gets the profile information for a user given their uid
		By: Parul Koul'''
	curs = conn.cursor(MySQLdb.cursors.DictCursor)
	curs.execute('SELECT * FROM user WHERE uid=%s;', [uid])
	profile = curs.fetchone()
	return profile

# ================================================================
# This starts the ball rolling, *if* the script is run as a script,
# rather than just being imported.    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {name} nm".format(name=sys.argv[0]))
    else:
        DSN = dbconn2.read_cnf()
        DSN['db'] = 'wprojdb_db'     # the database we want to connect to
        dbconn2.connect(DSN)
	print(lookupByNM(sys.argv[1]))
