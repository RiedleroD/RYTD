import sys, os

print("Trying to install requirements")

if os.system(sys.executable + " -m pip -q install --upgrade mysql-connector") != 0:
    print("Failed to install required package \"mysql-connector\" via pip.")
    sys.exit()

print("mysql-connector ist ready")

import mysql

