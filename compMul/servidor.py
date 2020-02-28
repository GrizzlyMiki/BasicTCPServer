import regex as reg
from pathlib import Path
import socket as socket
import user
import constants
import IO as io

#List with the current users registered
userDB = []
#We define the conection here as we want to allow every function to send data to the client
conection = None

#Regex pattern templates for the requests we expect to receive
requestPattern = r'(REG|MOD|DEL|GET|LST|CLOSE) ?(.*)?'
nickPattern = r'[a-zA-Z\_][a-zA-Z\_0-9]*'
IPPattern =  r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
portPattern = r'\d{1,4}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5]'

#The patterns for the expected requests
REGPattern = r'(' + nickPattern + r') (' + IPPattern + r') (' + portPattern + r')'
MODPattern = REGPattern
DELPattern = r'(' + nickPattern + r')'
GETPattern = DELPattern
userInDB = REGPattern + r'\n?'

#Compiled Regex expressions
request_ER = reg.compile(requestPattern)
REG_ER = reg.compile(REGPattern)
MOD_ER = reg.compile(MODPattern)
DEL_ER = reg.compile(DELPattern)
GET_ER = reg.compile(GETPattern)
userInDB_ER = reg.compile(userInDB)

#Fills the userDB list with the data from the DB file
def loadUserDB():
	#First we create a path that is independent of the OS
	fileRoute = Path(constants.DEFAULT_USERDB_FILEROUTE)
	try:
		#We open the file, if we do not find a file we will just leave the list empty
		file = open(fileRoute, 'r')
	except FileNotFoundError:
		return
	#At last, we will create and append a new user for each lane in the file
	nLines = file.readlines()
	for line in nLines:
		#The last line given by readlines() is an empty one, ourn Regex ER would fail without this
		if(line == ""):
			return
		result = userInDB_ER.fullmatch(line)
		newUser = user.User(result.group(1), result.group(2), result.group(3))
		userDB.append(newUser)

#Fills the userDB file with all the users which are actually on our list
def writeUserDB():
	#First we create a path that is independent of the OS
	fileRoute = Path(constants.DEFAULT_USERDB_FILEROUTE)
	try:
		#We open the file, if we do not find the path the program will end
		file = open(fileRoute, 'w+')
	except FileNotFoundError:
		print('Path to user database file not found.')
		exit
	#For each user in the list, we write it
	for user in userDB:
		file.write(user.nick + " " + user.ip + " " + user.puerto + "\n")

#Function which handles the received of the requests and acts as a controller
def atenderPeticion():
	#First we receive the request and we check it's syntax
	mensaje = io.receive(conection[0])
	result = request_ER.fullmatch(mensaje)
	#If the request is malformed, we tell the client and wait for a new one
	if (result == None):
		io.send(conection[0], 'ERROR\nMalformed request.\n')
		return
	operacion = result.group(1)
	if (operacion == None):
		io.send(conection[0], 'ERROR\nMalformed operation parameter.\n')
		return
	peticion = result.group(2)

	#Now we use a switch sentence to apply the desired operation
	if (operacion == "REG"):
		atenderREG(peticion)
	elif (operacion == "MOD"):
		atenderMOD(peticion)
	elif (operacion == "DEL"):
		atenderDEL(peticion)
	elif (operacion == "GET"):
		atenderGET(peticion)
	elif (operacion == "LST"):
		atenderLST()
	elif (operacion == "CLOSE"):
		io.send(conection[0], 'OK\n')
		return 0
	#If no operation is found we will tell the client and wait for a new request
	else:
		io.send(conection[0], 'ERROR\nOperation not defined.\n')

#Operation for registering new users
def atenderREG(peticion):
	#First we create the user with the info in the request
	result = REG_ER.fullmatch(peticion)
	newUser = user.User(result.group(1), result.group(2), result.group(3))
	#Now we add it to the list and answer the client
	userDB.append(newUser)
	io.send(conection[0], 'OK\n')

#Operation for modifying existing users
def atenderMOD(peticion):
	respuesta = 'OK\n'
	result = MOD_ER.fullmatch(peticion)
	#First we create a user that would be considered "equal" to the one we want to modify
	newUser = user.User(result.group(1), constants.DEFAULT_IP, constants.DEFAULT_PORT)
	try:
		#Now we get the index of the real one
		index = userDB.index(newUser)
		#Now we modify it thanks to the reference
		userDB[index].modify(result.group(1), result.group(2), result.group(3))
	except ValueError:
		respuesta = 'ERROR\nUser ' + result.group(1) + ' doesn\'t exist.\n'
	io.send(conection[0], respuesta)

#Operation for deleting an existing user
def atenderDEL(peticion):
	result = DEL_ER.fullmatch(peticion)
	#First we create a user that would be considered "equal" to the one we want to erase
	newUser = user.User(result.group(1), constants.DEFAULT_IP, constants.DEFAULT_PORT)
	respuesta = 'OK\n'
	try:
		#Now we tell the list to remove his equal
		userDB.remove(newUser)
	except ValueError:
		respuesta = 'ERROR\nUser ' + result.group(1) + ' doesn\'t exist.\n'
	io.send(conection[0], respuesta)

#Function to serve the client with the desired user
def atenderGET(peticion):
	result = GET_ER.fullmatch(peticion)
	target = result.group(1)
	salida = 'ERROR\nUser not found.\n'
	#We iterate the list looking for the desired nickname and we send it 
	for user in userDB:
		if user.nick == target:
			salida = str(user)
	#Weren't we able to find it, we would just send an error message
	io.send(conection[0], salida)

#Operation for listing all the users
def atenderLST():
	#We just map every user with it's string and we join these strings
	list = '\n'.join(map(str, userDB))
	io.send(conection[0], 'OK\n' + list + '\n')

if __name__ == '__main__':
	#First we load our user DB
	loadUserDB()
	#Now we create the socket with IPv4 and TCP 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#Now we bind it to port 80 and start listening for requests
	sock.bind(('', 80))
	sock.listen(5)
	#Now we accept the conection and we serve the requests
	conection = sock.accept()
	while(True):
		#The function atenderPeticion() will return None unless the request CLOSE is received
		if (atenderPeticion() != None):
			sock.close
			#Only when we close we write the actual user list to the DB
			writeUserDB()
			break
