import psycopg2
import sys

try:
	conn = psycopg2.connect("dbname='cs421' user='cs421g29' host='comp421.cs.mcgill.ca' password='ChickenNugge1s'")
except:
	print "Could not connect"

cur = conn.cursor()

loginvar = 0
provar = 0

def login(uname, passwd):
	global loginvar, provar
	userpasswordq = """SELECT * FROM "User" WHERE username='{%s}' AND password='{%s}';"""
	prouserq = """SELECT * FROM "prouser" WHERE username='{%s}';"""

	cur.execute(userpasswordq % (uname,passwd))
	try:
		cur.fetchone()[0]
		loginvar = 1
		print "You have been logged in!"
		cur.execute(prouserq %(uname))
		try:
			cur.fetchone()[0]
			provar = 1
		except:
			pass

	except:
		print "Invalid username/password. Please try again."

	print provar


def logout():
	global loginvar, provar
	if(loginvar==0):
		print "You are already logged out."
	else:
		loginvar = 0
		provar = 0
		print "You have successfully logged out."

def signup(new_email, new_uname, new_passwd):
	addUsrPassq = """INSERT INTO "User" (username, password, email) VALUES ({%s}, {%s}, {%s}); """
	cur.execute(addUsrPassq % (new_uname, new_passwd, new_email))


	

if __name__ == '__main__':
	while(1):
    	#print "Choose Login or Signup:"
		choice = raw_input()
		if(choice == "Login"):
			if(loginvar==0):
				print "Please enter your username:"
				username = raw_input()
				print "Please enter your password:"
				password = raw_input()
				login(username,password)


			elif(loginvar==1):
				print "Would you like to log out? [y/n]"
				ans = raw_input()
				if ans=='y':
					logout()
				elif ans=='n':
					print "Would you like to terminate your session? [y/n]"
					ans = raw_input()
					if ans=='y':
						sys.exit()
		elif(choice == "Signup"):
    			print "Please enter your email"
			email = raw_input()
			print "Please enter your username:"
			username = raw_input()
			print "Please enter your password:"
			password = raw_input()
			signup(email, username, password)