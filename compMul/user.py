#This class defines a user for our basic TCP server
class User:
    def __init__(self, nick, ip, puerto):
        self.nick = nick
        self.ip = ip
        self.puerto = puerto
    
    def __eq__(self, other):
        return self.nick == other.nick

    def __str__(self):
        return 'Nick: ' + self.nick + " IP: " + self.ip + " Port: " + str(self.puerto)
        
    #Althought this function is not neccesary we define it 
    def modify(self, nick, ip, puerto):
        self.nick = nick
        self.ip = ip
        self.puerto = puerto

if __name__ == '__main__':
    print('This class is not intended to be the main module')