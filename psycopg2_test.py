import psycopg2
import sys

try:
	conn = psycopg2.connect("dbname='cs421' user='cs421g29' host='comp421.cs.mcgill.ca' password='ChickenNugge1s'")
except:
	print "Could not connect"

cur = conn.cursor()

loginvar = 0
def login(uname, passwd):
	global loginvar
	myquery = """SELECT * FROM "User" WHERE username='{%s}' AND password='{%s}';"""

	cur.execute(myquery % (uname,passwd))
	try:
		cur.fetchone()[0]
		loginvar = 1
		print "You have been logged in!"	
	except Exception as e:
		print "Invalid username/password. Please try again."

def logout():
	global loginvar
	if(loginvar==0):
		print "You are already logged out."
	else:
		loginvar = 0
		print "You have successfully logged out."

if __name__ == '__main__':
	while(1):
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