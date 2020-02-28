import os
import sys
#File with constant definitions for the basic TCP server

DEFAULT_IP = '0.0.0.0'
DEFAULT_PORT = 0
DEFAULT_USERDB_FILEROUTE = os.path.join(sys.path[0], "userDB.txt")


if __name__ == '__main__':
    print('This class is not intended to be the main module')