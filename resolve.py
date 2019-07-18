import socket, sys, os, sqlite3

if os.system(sys.executable + " -m pip install mysql-connector") != 0:
    print("Failed to install required package \"mysql-connector\" via pip.")
    sys.exit()

import mysql