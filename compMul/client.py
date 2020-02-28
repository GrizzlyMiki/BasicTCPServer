import regex as reg
import socket as socket
import constants
import IO as io

if __name__ == '__main__':
    #First we create the socket on IPv4 and using TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #Now we connect with the TCP server
        sock.connect(("", 80))
    except OSError as e:
        print(e)
    while(True):
        #User will write the command he want to send to the user
        command = input('Escribe el comando a enviar al servidor:')
        #Now we send it to the server
        io.send(sock, command)
        #We wait for the response to print it
        print(io.receive(sock))
        #If the command was the one meant to close all communication, we end the execution
        if (command == "CLOSE"):
            break