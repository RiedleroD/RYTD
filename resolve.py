import socket, sys, os, sqlite3

print("Trying to install mysql-connector")

if os.system(sys.executable + " -m pip -q install --upgrade mysql-connector") != 0:
    print("Failed to install required package \"mysql-connector\" via pip.")
    sys.exit()

print("mysql-connector ist ready")

import mysql