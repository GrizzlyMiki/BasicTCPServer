import socket as socket

#Functional class we use to send and receive data through the sockets

#Function used to receive a string from the socket
def receive(sock):
	chunks = []
	bytesRecv = 0
	#First we receive a header of 4B with the length of the message
	head = sock.recv(4)
	msglen = int.from_bytes(head,byteorder='big')
	msglen = socket.ntohl(msglen)
	#Now we keep doing partial reads until we read that full length or we get an error
	while bytesRecv < msglen:
		chunk = sock.recv(min(msglen - bytesRecv, 2048))
		if chunk == b'':
			raise RuntimeError("socket connection broken")
		#We hoard every chunk we receive
		chunks.append(chunk)
		bytesRecv = bytesRecv + len(chunk)
	#Now we join all those chunks to create the output string
	return str(b''.join(chunks), 'utf-8')

#Function for sending a string through the socket
def send(sock, msg):
	msg = msg.encode('utf-8')
	totalsent = 0
	#First we calculate the full length of the string and we send it as our header
	msglen = len(msg)
	header = socket.htonl(len(msg))
	sock.send(header.to_bytes(4, byteorder='big'))
	#Now we keep sending partial data until we send as much data as we adviced on the header
	while totalsent < msglen:
		sent = sock.send(msg[totalsent:])
		#If we send 0 we got an error
		if sent == 0:
			raise RuntimeError('socket connection broken')
		totalsent = totalsent + sent

if __name__ == '__main__':
    print('This class is not intended to be the main module')