import psycopg2
import random
import sys
import datetime as dt


try:
	conn = psycopg2.connect("dbname='cs421' user='cs421g29' host='comp421.cs.mcgill.ca' password='ChickenNugge1s'")
except:
	print "Could not connect"

cur = conn.cursor()

loginvar = 0
provar = 0
current_user = ''

def getID(table, column):
	try:
		latestID = """SELECT MAX("%s") FROM "%s";"""
		cur.execute(latestID % (column, table))
		output = int(cur.fetchone()[0])
		return output
	except: 
		return 1

def getDate():
	date = dt.datetime.now().strftime('%Y-%m-%d')
	# i = dt.datetime.now()
	# date = "%d-%02d-%02d" % (i.year,i.month,i.day)
	return date

def login(uname, passwd):
	global loginvar, provar, current_user
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

def signup(new_email, new_uname, new_passwd, proUser_yOrN, bank_name):
	#Queries
	addUsr = """INSERT INTO "User" ("username", "password", "email") VALUES ('{%s}', '{%s}', '{%s}');"""
	addProUsr = """INSERT INTO "prouser" ("username", "Rating") VALUES ('{%s}', %d); """
	addBank = """INSERT INTO "Account" ("accountNumber", "bankName") VALUES (%d, '{%s}'); """
	setupDW = """INSERT INTO "DigitalWallet" ("dwID", "Bitcoin") VALUES (%d, %d);"""
	transferProUsrPayment = """INSERT INTO "transfers" ("accountNumber", "dwID", "TransID") VALUES (%d, %d, %d);"""
	ProUsrPayment = """INSERT INTO "transaction" ("TransID","amount","tDate","TransType") VALUES ('{%s}', %d, (TIMESTAMP '{%s}'), '{%s}'); """
	updateDigitalWallet = """UPDATE "DigitalWallet" SET "Bitcoin"=%d WHERE "dwID"=%d; """
	#Getters
	newDwID = getID("DigitalWallet", "dwID")+1
	newAccountNumber = getID("Account","accountNumber")+1
	newTransactionID = getID("transaction","TransID")+1
	print newDwID
	print newAccountNumber
	print newTransactionID
	#Actual Setup 
	cur.execute(addUsr % (new_uname, new_passwd, new_email))
	conn.commit()#create the user

	cur.execute(addBank % ((newAccountNumber), bank_name))
	conn.commit()#create the Account

	cur.execute(setupDW % (newDwID, 0))
	conn.commit()#create the DigitalWallet

	if(proUser_yOrN==1):
		cur.execute(addProUsr % (new_uname, 0))
		conn.commit()#add user to pro user table

		cur.execute(updateDigitalWallet % (-10, newDwID))
		conn.commit()#charge digitalWallet for payment 

		print "Would you like to pay [NOW] or [LATER] ?"
		answer = raw_input()
		if(answer=="NOW"):
			cur.execute(transferProUsrPayment % (newAccountNumber, newDwID, newTransactionID))
			conn.commit()#acknowledge a transfer for the ProUsrPayment

			cur.execute(ProUsrPayment % (newTransactionID, 10, getDate, "withdraw"))
			conn.commit()#create the payment transaction

			cur.execute(updateDigitalWallet % (newDwID, 0))
			conn.commit()#update digital wallet
		
		print "Your account "

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
	owner_dwID = 0
	secretInfo = []
	yyyy_mm_dd = getDate()
	# Our Queries
	get_secretInfo = """SELECT "price","description" FROM "secretPosting" WHERE "sID"=%d;"""
	get_dwID = """SELECT "dwID" FROM "Owns" WHERE "username"='{%s}';"""
	get_owner_dwID = """SELECT "dwID" FROM "pSell" WHERE "sID"=%d;"""
	get_Bitcoin = """SELECT "Bitcoin" FROM "DigitalWallet" WHERE "dwID"=%d; """
	update_Bitcoin = """UPDATE "DigitalWallet" SET "Bitcoin"=%d WHERE "dwID"=%d;"""
	update_buysecret = """INSERT INTO "buysecret" ("sID","dwID","username") VALUES (%d,%d,'{%s}');"""
	update_transaction = """INSERT INTO "transaction" ("TransID","amount","tDate","TransType") VALUES (%d,%d,'%s','%s');"""

	cur.execute(get_secretInfo % secretID)
	# try:
	secretInfo = cur.fetchone()

	print "Price: %d" % (secretInfo[0])
	print "Description: %s" % (secretInfo[1])

	cur.execute(get_owner_dwID % secretID)
	try:
		owner_dwID = int(cur.fetchone()[0])
	except:
		pass

	cur.execute(get_dwID % current_user)
	try:
		myWallet = int(cur.fetchone()[0])
	except:
		print "Oops! Your digital wallet could not be loaded."

	cur.execute(get_Bitcoin % myWallet)
	btc = 0
	
	try:
		btc = int(cur.fetchone()[0])
	except:
		print "You don't seem to have any money in this wallet."

	if btc > secretInfo[0]:		# Check that the user has enough money
		# Remove btc from our wallet
		new_btc = btc - secretInfo[0]
		cur.execute(update_Bitcoin % (new_btc, myWallet))
		conn.commit()

		# Add btc to owner's wallet
		cur.execute(get_Bitcoin % owner_dwID)
		try:
			owner_new_btc = btc + cur.fetchone()[0]
			cur.execute(update_Bitcoin % (owner_new_btc, owner_dwID))
			conn.commit()
		except:
			pass

		# Update the transaction table
		# try:
		user_tID = int(getID("Transaction","TransID")+1)
		owner_tID = getID("Transaction","TransID")+1
		print(update_transaction % (user_tID, secretInfo[0], str(yyyy_mm_dd), 'withdraw'))
		cur.execute(update_transaction % (user_tID, secretInfo[0], str(yyyy_mm_dd), 'withdraw'))
		conn.commit()
		cur.execute(update_transaction % (owner_tID, secretInfo[0], yyyy_mm_dd, 'deposit'))
		conn.commit()
		# except:
		# 	print "Error updating the transaction table."

		# Update the buysecret table
		cur.execute(update_buysecret % (secretID, myWallet, current_user))
		conn.commit()

		print "Purchase successful!"
			
	else:
		print "Oops! You don't have enough money."
	# except:
	# 	print "No such secret"

def sell_secret(price, encryptInfo, description):
	update_Sellings = """INSERT INTO "Sellings" VALUES (%d);"""
	update_pSell = """ INSERT INTO "pSell" VALUES (%d,%d,'{%s}',%d);"""
	update_secretPosting = """INSERT INTO "secretPosting" VALUES (%d, %d, '%s', '{%s}');"""
	get_dwID = """SELECT "dwID" FROM "Owns" WHERE "username"='{%s}';"""
	#Things to do in this function
	#	Update pSell, Sellings
	#	Update the secretPosting table with args
	if (provar==0):
		print "I'm sorry, but you are unable to sell secrets.\n Please become a pro user to do so."
	else:
		my_sellID = makeID("Sellings","sellID")
		my_sID = makeID("secretPosting","sID")
		cur.execute(get_dwID % current_user)
		try:
			my_dwID = cur.fetchone()[0]
		except:
			print "Your digital wallet could not be found!"

		# Update secretPosting --> sID, [[args]]
		cur.execute(update_secretPosting % (my_sID, price, encryptInfo, description))
		conn.commit()

		# Update Sellings --> sellID
		cur.execute(update_Sellings % my_sellID)
		conn.commit()

		# Update pSell --> sID, dwID, username, sellID
		cur.execute(update_pSell % (my_sID, my_dwID, current_user, my_sellID))
		conn.commit()
		print "Your listing has been posted!"
                
if __name__ == '__main__':
	check_wallet_query = """"""
	display_secrets_query = """SELECT "sID","description","price" FROM "secretPosting";"""

	while(1):
		if(loginvar==0):
			print "Choose Login, Signup, or Exit:"

			choice = raw_input()

			if(choice == "Login"):
				print "Please enter your username:"
				username = raw_input()
				print "Please enter your password:"
				password = raw_input()
				login(username,password)

			elif(choice == "Signup"):
				print "Please enter your email"
				email = raw_input()
				print "Please enter your username:"
				username = raw_input()
				print "Please enter your password:"
				password = raw_input()
				print "Would you like to be a pro user? yes/no"
				am_pro = raw_input()
				print "Please enter your bank name:"
				my_bank = raw_input()
				if(am_pro=="yes"):
					signup(email, username, password, 1, my_bank)
				else:
					signup(email, username, password, 0, my_bank)
				login(username,password)
				print "You are now signed up! Enjoy using the site.\n"

			elif(choice == "Exit"):
				print "Goodbye!"
				sys.exit()

			else:
				print "Please input a valid option (remember: options are cAse SenSiTiVe):"

		elif(loginvar==1):
			print "What would you like to do?"
			if(provar==0):
				print "[buy secret][check wallet][logout]"
			elif(provar==1):
				print "[buy secret][sell secret][check wallet][logout]"

			ans = raw_input()

			if(ans=="buy secret"):
				print "Available secrets:"
				cur.execute(display_secrets_query)
				try:
					avail_secrets = cur.fetchall()
					print '%-15s' '%-45s' '%s' % ("Secret ID","Description","Price")
				except:
					print "Error: Could not load secrets."
				for item in avail_secrets:
					print '%-15s' '%-45s' '%s' % (str(item[0]), str(item[1]), str(item[2]))
				print "Please enter the ID for the secret you'd like to purchase:"

				sID_to_buy = int(raw_input())

				buy_secret(sID_to_buy)

			elif(ans=="sell secret"):
				print "Please write the secret below:"
				my_encryptinfo = raw_input()
				print "Please give a brief description of the secret:"
				my_desc = raw_input()
				print "Please enter a price for your secret:"
				my_price = raw_input()

				sell_secret(float(my_price), my_encryptinfo, '{my_desc}')

			elif(ans=="check wallet"):
				print "You have X bitcoin"
			elif(ans=="logout"):
				print "You have logged out"
				loginvar = 0
				provar = 0
				current_user = ''
			else:
				print "Please enter a valid input."

