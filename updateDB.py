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

#TO DO: Insert Functions Below

# def addUser(conn,):
# 	conn = dbconn2.connect(dsn)
#     curs = conn.cursor(MySQLdb.cursors.DictCursor)
#     curs.execute('SELECT username FROM userpass WHERE username = %s',
#                      [username])
#     return curs.fetchone()

# def addProject(conn, projCreator, projName, projDur, projComp, projRoles, projReq, projDesc)
# 	curs = conn.cursor(MySQLdb.cursors.DictCursor) # results as Dictionaries
#     curs.execute('insert into project (creator, name, compensation, rolesOpen, \
#     	description, duration) values (%s, %s, %s, %s, %s, %s)', [projCreator, \
#     	projName, projDur, projComp, projRoles, projReq, projDesc])
#     return "Project created"


# ================================================================
# This starts the ball rolling, *if* the script is run as a script,
# rather than just being imported.    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: {name} nm".format(name=sys.argv[0])
    else:
        DSN = dbconn2.read_cnf()
        DSN['db'] = 'wprojdb_db'     # the database we want to connect to
        dbconn2.connect(DSN)
        print lookupByNM(sys.argv[1])