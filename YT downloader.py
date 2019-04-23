import pytube, os, sys, io, mutagen, json
#
#POSSIBLE ARGS:
#	--conf
#		triggers configuration and then quits
#	--help
#		shows help
#	--overwrite
#		download and convert videos even if existent.
#	<link>
#		a link. (youtube only) 
#
class Vid(pytube.YouTube):
	def ineed(self):
		self.name=self.title
		self.i=self.video_id
def singvid(link):
	link=link.split("&")[0]
	print(link)
	yt=Vid(link)
	yt.ineed()
	print(yt.name)
	streams=yt.streams
	print("All streams:\n",streams.all())
	stream=streams.first()
	print("Selected Stream:\n",stream)
	filename=strip(yt.title,yt.i)
	stream.download(output_path=conf.curdir,filename=filename)
	print("Converting...")
	convert(conf.curdir+"/"+filename)
	print("Finished")
def stuff(vid):
	vid.ineed()
	sys.stdout.write("\033[s"+strip(vid.title)[0])
	sys.stdout.flush()
	filename=strip(vid.title,vid.i)
	print("\033[7m[Downloading]\033[0m"," "*10,end="\033[24D")
	sys.stdout.flush()
	try:	
		vid.streams.first().download(output_path=conf.curdir,filename=filename)
	except Exception as e:
		if e is KeyboardInterrupt:
			quit()
		else:
			print(" \033[7m\033[31m[Failed1]\033[0m",e,end=" "*10+"\n\r")
			conf.stats[False]+=1
	else:
		print("\033[7m[Converting]\033[0m"," "*10,end="\033[23D")
		sys.stdout.flush()
		try:
			convert(conf.curdir+"/"+filename,ext=None)
		except KeyboardInterrupt:
			quit()
		#except Exception as e:
		#	print(" \033[7m\033[31m[Failed2]\033[0m",e,end=" "*10+"\n\r")
		#	conf.stats[False]+=1
		else:
			sys.stdout.write(" \033[7m\033[32m[Finished]\033[0m          \n\r")
			conf.stats[True]+=1
	sys.stdout.flush()
def playlist(link,files):
	#https://www.youtube.com/playlist?list=PLk5KkYG8je9DsAgKQcRrT9wOlTHiJmORl
	sys.stdout.write("Checking...\r")
	links=pytube.Playlist(link).parse_links()
	for link in links:
		i=link.split("?v=")[-1]
		sys.stdout.write(str(links.index(link)+1)+"/"+str(len(links))+": youtube.com"+link+": \033[7m[Checking...]\033[27m\033[13D")
		sys.stdout.flush()
		if (not i in conf.files) or ("--overwrite" in sys.argv):
			try:
				vid=Vid("youtube.com"+link)
			except KeyboardInterrupt:
				raise KeyboardInterrupt()
			except Exception as e:
				sys.stdout.write("\033[7m\033[31m[Failed, trying again...]\033[0m\033[25D")
				sys.stdout.flush()
				try:
					vid=Vid("youtube.com"+link)
				except KeyboardInterrupt:
					raise KeyboardInterrupt()
				except Exception as e:
					sys.stdout.write("\033[7m\033[31m[Failed3]\033[0m"+" "*16+"\n\r")
				else:
					stuff(vid)
			else:
				stuff(vid)
		else:
			sys.stdout.write("\033[s\033[7m[Exists]\033[27m     \n\r")
			conf.stats[None]+=1
def strip(s,i=0):
	s=s.replace(".","\u2024")
	s=s.replace("/","\u2215")
	s=s.replace("\"","\u1426")
	s=s.replace("#","\u2d4c")
	s=s.replace(":","\u0589")
	s=s.replace("\\","\u29f5")
	s=s.replace("\'","\u02c8")
	s=s.replace("*","\u2217")
	s=s.replace("?","\u1e92")
	s=s.replace(",","\u02cc")
	s=s.replace("~","\u1513")
	s=s.replace("|","\u05c0")
	if i==0:
		if "\u2020" in s:
			i,s=s.split("\u2020")
		return s,i
	else:
		return str(i)+"\u2020"+s
class Config():
	def __init__(self):
		self.curdir=os.path.abspath(os.path.dirname(__file__))
		self.links=[]
		self.files={}
		self.conffile=self.curdir+"/.rytdconf"
		self.stats={True:0,None:0,False:0}
	def load(self):
		status=self.load_from_file(self.curdir)
		self.load_files()
		self.load_link()
		self.dump(self.conffile)
	def load_files(self):
		for dirpath, dirnames, filenames in os.walk(self.curdir):
			for f in filenames:
				name,i=strip(os.path.splitext(f)[0])
				try:
					i=mutagen.File(dirpath+"/"+f)["description"][0]
				except TypeError:
					pass
				except KeyError:
					pass
				if i!=0:
					self.files[i]=name
	def load_link(self):
		link=None
		for arg in sys.argv:
				if "/watch?v=" in arg or "/playlist?list=" in arg:
					link=arg
		if self.links==[]:
			if self.links==[] and link==None:
				link=input("Link please. (Single video or full playlist)\n")
			elif link!=None:
				self.links=[link]
	def load_from_file(self,path):
		found=False
		for dirpath, dirnames, filenames in os.walk(path):
			for f in filenames:
				if f.startswith(".rytdconf"):
					found=True
					conffile=open(dirpath+"/"+f,"r")
					try:
						sett=json.load(conffile)
					except json.decoder.JSONDecodeError:
						print("NO CONFIG FILE FOUND OR FILE EMPTY")
						self.set_tings()
					finally:
						conffile.close()
					for link in sett["links"]:
						self.links.append(link)
		if found==False:
			self.set_tings()
	def set_tings(self):
		f=self.curdir+"/.rytdconf"
		inpot=""
		while not inpot in ("EOF","\"EOF\""):
			inpot=input("Paste one Link at a time in here, and finish the input with \"EOF\".\n")
			if not inpot in ("EOF","\"EOF\""):
				self.links.append(inpot)
		
		self.dump(f)
		quit()
	def dump(self,f):
		sett={
			"conffile":self.conffile,
			"links":self.links}
		conffile=open(f,"w+")
		try:
			json.dump(sett,conffile)
		finally:
			conffile.close()
def convert(f,ext):
	if f.endswith(".mp4") or f.endswith(".webm") or f.endswith(".mkv"):
		fn,ext=os.path.splitext(f)
	elif ext==None:
		for ext in (".mp4",".mkv",".webm"):
			tryagain=False
			success=False
			try:
				convert(f,ext)
			except OSError:
				tryagain=True
			else:
				success=True
			if success or not tryagain:
				break
		if not success:
			raise OSError("File doesn't exist. "+f)
		else:
			return
	else:
		f+=ext
	if not os.path.exists(f):
		raise OSError("File doesn't exist. "+f)
	elif os.path.isfile(f):
		dirpath,f=os.path.split(f)
	else:
		if os.path.isdir(f):
			raise TypeError("Expected a file, got a directory.")
		elif os.path.islink(f):
			raise TypeError("Expected a file, got a Link.")
		elif os.path.ismount(f):
			raise TypeError("Expected a file, got a mount point.")
	if "\u2020" in f:
		i,f=os.path.splitext(f)[0].split("\u2020")
		command="ffmpeg -v 0 -i \""+dirpath+"/"+i+"\u2020"+f+ext+"\" -vn -y -metadata comment=\""+i+"\" \""+dirpath+"/"+f+".ogg\""
		excode=os.system(command)
		os.remove(dirpath+"/"+i+"\u2020"+f+ext)
		if excode==0:
			pass
		elif excode==2:
			raise KeyboardInterrupt()
		else:
			raise Exception("Exited with errcode \033[1m"+str(excode)+"\033[0m\n"+str(command))
def main():
	global conf
	conf=Config()
	conf.load()
	if "--conf" in sys.argv:
		conf.set_tings()
		quit()
	if "--help" in sys.argv:
		print("--conf       Triggers configuration and quits after this.\n--help       Triggers help and quits.\n--overwrite  overwrites all previously downloaded files (WARNING: This may result in really long waiting and massive Data usage.)")
		quit()
	manmode=False
	for arg in sys.argv:
		if "/watch?v=" in arg:
			singvid(arg)
			manmode=True
		elif "/playlist?list=" in arg:
			playlist(arg)
			manmode=True
	if manmode:
		quit()
	try:
		for link in conf.links:
			if "/watch?v=" in link:
				singvid(conf.link)
			elif "/playlist?list=" in link:
				playlist(link,conf.files)
			else:
				raise ValueError("Invalid link type")
		sys.stdout.write("Finished\n")
		sys.stdout.flush()
	finally:
		print("\nDownloaded: "+str(conf.stats[True])+"\nExisting: "+str(conf.stats[None])+"\nFailed: "+str(conf.stats[False]))
if __name__=="__main__":
	main()
