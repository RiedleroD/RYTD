import os, sys
curdir=os.path.abspath(os.path.dirname(__file__))
for dirpath, dirnames, filenames in os.walk(curdir):
	for f in filenames:
		if f.endswith(".mp4"):
			video=True
			ext=".mp4"
		elif f.endswith(".webm"):
			video=True
			ext=".webm"
		else:
			video=False
			ext=None
		if video and "\u2020" in f:
			i,f=os.path.splitext(f)[0].split("\u2020")
			command="ffmpeg -v 0 -i \""+dirpath+"/"+i+"\u2020"+f+ext+"\" -vn -y -metadata comment=\""+i+"\" \""+dirpath+"/"+f+".ogg\""
			print(command)
			excode=os.system(command)
			if excode==0:
				os.remove(dirpath+"/"+i+"\u2020"+f+ext)
			elif excode==2:
				raise KeyboardInterrupt()
			else:
				print("\033[31mExited with errcode \033[1m"+str(excode)+"\033[0m")
