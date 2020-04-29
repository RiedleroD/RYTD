import sys, os

print("Trying to install requirements")

required_packages = ["pytube", "mutagen", "youtube_dl"]

for requirement in required_packages:
    print("Trying to install \"" + requirement + "\"")
    if os.system(sys.executable + " -m pip -q install --upgrade " + requirement) != 0:
        print("Failed to install required package \"" + requirement + "\" via pip.")
        sys.exit(1)
    print("\"" + requirement + "\" ist ready")
