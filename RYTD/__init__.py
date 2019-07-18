import sys, os

print("Trying to install requirements")

requirements = ["mysql-connector"]

for requirement in requirements:
    print("Trying to install \"" + requirement + "\")
    if os.system(sys.executable + " -m pip -q install --upgrade " + requirement) != 0:
        print("Failed to install required package \"" + requirement + "\" via pip.")
        sys.exit()
    print("\"" + requirement + "\" ist ready")
