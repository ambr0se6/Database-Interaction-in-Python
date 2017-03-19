import psycopg2
import random
import sys

try:
	conn = psycopg2.connect("dbname='cs421' user='cs421g29' host='comp421.cs.mcgill.ca' password='ChickenNugge1s'")
except:
	print "Could not connect"

cur = conn.cursor()

loginvar = 0
provar = 0
current_user = ''

def makeID():
	return random.randint(0,2147483647)

def login(uname, passwd):
	global loginvar, provar
	userpasswordq = """SELECT * FROM "User" WHERE username='{%s}' AND password='{%s}';"""
	prouserq = """SELECT * FROM "prouser" WHERE username='{%s}';"""

	cur.execute(userpasswordq % (uname,passwd))
	try:
		cur.fetchone()[0]
		loginvar = 1
		current_user = uname
		print "You have been logged in!"
		cur.execute(prouserq %(uname))
		try:
			cur.fetchone()[0]
			provar = 1
		except:
			pass

	except:
		print "Invalid username/password. Please try again."

	# print provar


def logout():
	global loginvar, provar
	if(loginvar==0):
		print "You are already logged out."
	else:
		loginvar = 0
		provar = 0
		current_user = ''
		print "You have successfully logged out."

def signup(new_email, new_uname, new_passwd):
	addUsrPassq = """INSERT INTO "User" ("username", "password", "email") VALUES ('{%s}', '{%s}', '{%s}'); """
	cur.execute(addUsrPassq % (new_uname, new_passwd, new_email))
	conn.commit()

def buy_secret(secretID):
	#Things to do in this function:
	#	Subtract the secret's "price" out of current_user's digital wallet
	#		Ask user the wallet out of which they'd like to pay
	#	Add the secret's price to its owner's digital wallet
	#	Update buysecret with user's info and secretID
	#	Ask user to fill out info for how they'd like the secret to be delivered.
	#		Check to see if by some divine intervention our makeID() is already taken
	#		Reroll if necessary.
	#	Update deliver table.
	myWallets = []
	owner_dwID = ''
	secretInfo = []
	# Our Queries
	get_secretInfo = """SELECT "price","description" FROM "secretPosting" WHERE "sID"=%d;"""
	get_dwIDs = """SELECT "dwID" FROM "Owns" WHERE "username"='{%s}';"""
	get_owner_dwID = """SELECT "dwID" FROM "pSell" WHERE "sID"=%d;"""
	get_Bitcoin = """SELECT "Bitcoin" FROM "DigitalWallet" WHERE "dwID"=%d; """
	update_Bitcoin = """UPDATE "DigitalWallet" SET "Bitcoin"=%d WHERE "dwID"=%d;"""
	
	cur.execute(get_secretInfo % secretID)
	try:
		secretInfo = cur.fetchone()
	except:
		print "No such secret"

	print "Price: %d" % (secretInfo[0])
	print "Description: %s" % (secretInfo[1])

	cur.execute(get_owner_dwID % secretID)
	try:
		owner_dwID = cur.fetchone()[0]
	except:
		pass

	cur.execute(get_dwIDs % current_user)
	try:
		myWallets = cur.fetchall()
	except:
		print "Oops! You don't have any digital wallets."

	print "Which wallet would you like to use? "
	for wallet in myWallets:
		print wallet

	wallet_to_use = raw_input()

	if wallet_to_use in myWallets:
		cur.execute(get_Bitcoin % wallet_to_use)
		btc = 0
		
		try:
			btc = cur.fetchone()[0]
		except:
			print "You don't seem to have any money in this wallet."

		if btc > secretInfo[0]:
			# Remove btc from our wallet
			new_btc = btc - secretInfo[0]
			cur.execute(update_Bitcoin % (new_btc, wallet_to_use))

			# Add btc to owner's wallet
			cur.execute(get_Bitcoin % owner_dwID)
			try:
				owner_new_btc = btc + cur.fetchone()[0]
				cur.execute(update_Bitcoin % (owner_new_btc, owner_dwID))
			except:
				pass

			# Update the buysecret table
			
			
		else:
			print "You don't have enough money in this wallet."


def sell_secret(price, encryptInfo, description):
	#Things to do in this function
	#	Update pSell, Sellings
	#	Update the secretPosting table with args

if __name__ == '__main__':
	while(1):
		print "Choose Login or Signup:"
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