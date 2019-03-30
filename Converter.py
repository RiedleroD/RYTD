import os, sys
curdir=os.path.abspath(os.path.dirname(__file__))
for dirpath, dirnames, filenames in os.walk(curdir):
	for f in filenames:
		if f.endswith(".mp4"):
			command="ffmpeg -n -v 0 -i \""+dirpath+"/"+f+"\" \""+dirpath+"/"+os.path.splitext(f)[0]+".ogg\""
			print(command)
			excode=os.system(command)
			if excode==0:
				os.remove(dirpath+"/"+f)
			else:
				print("\033[31mExited with errcode \033[1m"+str(excode)+"\033[0m")
