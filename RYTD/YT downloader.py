import pytube, os, sys, io, mutagen, json
from youtube_dl import YoutubeDL as YDL
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
def sprint(*s:str,sep:str="",end:str="",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)
def sprintn(*s:str,sep:str="",end:str="\n\r",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)
def sprintr(*s:str,sep:str="",end:str="\r",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)

class Vid(pytube.YouTube):
	def ineed(self,verbose=False):
		if verbose:
			print("Video initialisation,")
			self.name=self.title
			print("self.name=",self.name)
			self.i=self.video_id
			print("self.i=",self.i)
		else:
			self.name=self.title
			self.i=self.video_id
def singvidhook(d):
	#'status': 				str<'downloading' | 'finished'>
	#'downloaded_bytes':	int<downloaded bytes>https://www.youtube.com/watch?v=Cof4IRv8Mhg
	#'total_bytes':			int<total bytes>
	#'tmpfilename':			str<tmp filename>
	#'filename':			str<filename>
	#'eta':					int<remaining time in seconds>
	#'speed':				flt<download speed>
	#'elapsed':				flt<elapsed time in seconds>
	#'_total_bytes_str':	str<total bytes>
	#'_elapsed_str':		str<elapsed time in seconds>
	#'_eta_str':			str<remaining time in seconds>
	stat=d['status']
	filename=d['filename']
	if stat=="downloading":
		print(filename,stat,d['_eta_str'],end="\033[u",flush=True)
	elif stat=="finished":
		print(filename,stat,d['_elapsed_str'],end="\n",flush=True)
	else:
		print("HOLY F A NEW STATUS JUST GOT RECOGNIZED:",stat,end="\n\033[s",flush=True)

def olsingvid(link,verbose=False):
	link=link.split("&")[0]
	print(link)
	yt=Vid(link)
	yt.ineed(verbose)
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
def stuff(vid,verbose=False):
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
def playlist(link,files,ydl,verbose=False):
	if verbose:
		sprintn("Checking...")
	else:
		sprintr("Checking...")
	links=pytube.Playlist(link).parse_links()
	if verbose:
		sprintn(links)
	for link in links:
		i=link.split("?v=")[-1]
		if verbose:
			sprintn("\n\033[44m",links.index(link)+1,"/",len(links),"\033[49m\n\033[43m",i,"\033[49m ")
		else:
			sprint(links.index(link)+1,"/",len(links),": youtu.be/",i,": \033[7m[Checking...]\033[27m\033[13D")
		if (not i in conf.files) or ("--overwrite" in sys.argv):
			try:
				ydl.download(["http://youtube.com"+link])
			except KeyboardInterrupt:
				raise KeyboardInterrupt()
			except:
				pass
		else:
			if verbose:
				sprintn("\033[7m[Exists]\033[0m")
			else:
				sprint("\033[s\033[7m[Exists]\033[27m",end="     \n\r")
			conf.stats[None]+=1
def olplaylist(link,files,verbose=False):
	if verbose:
		sprintn("Checking")
	else:
		sprintr("Checking...")
	links=pytube.Playlist(link).parse_links()
	if verbose:
		sprintn(links)
	for link in links:
		i=link.split("?v=")[-1]
		if verbose:
			print("\n\033[44m",links.index(link)+1,"/",len(links),"\033[49m\n\033[43m",i,"\033[49m ",sep="",flush=True)
		else:
			print(links.index(link)+1,"/",len(links),": youtu.be/",i,": \033[7m[Checking...]\033[27m\033[13D",sep="",end="",flush=True)
		if (not i in conf.files) or ("--overwrite" in sys.argv):
			try:
				vid=Vid("youtube.com"+link)
			except KeyboardInterrupt:
				raise KeyboardInterrupt()
			except Exception as e:
				print("\033[7m\033[31m[Failed, trying again...]",end="\033[0m\033[25D",flush=True)
				try:
					vid=Vid("youtube.com"+link)
				except KeyboardInterrupt:
					raise KeyboardInterrupt()
				except Exception as e:
					if verbose:
						print("\033[7m\033[31m[Failed3]\033[0m",e,flush=True)
					else:
						print("\033[7m\033[31m[Failed3]\033[0m"+" "*16,end="\n\r",flush=True)
				else:
					stuff(vid)
			else:
				stuff(vid)
		else:
			if verbose:
				print("\033[7m[Exists]\033[0m",flush=True)
			else:
				print("\033[s\033[7m[Exists]\033[27m",end="     \n\r",flush=True)
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
	s=s.replace(";","\u037e")
	if i==0:
		if "\u2020" in s:
			i,s=s.split("\u2020")
		return s,i
	else:
		return str(i)+"\u2020"+s
class Config():
	def __init__(self):
		self.curdir=os.path.abspath(os.path.dirname(__file__))
		os.chdir(self.curdir)
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
		try:
			while not inpot in ("EOF","\"EOF\""):
				inpot=input("Paste one Link at a time in here, and finish the input with \"EOF\".\n")
				if not inpot in ("EOF","\"EOF\""):
					self.links.append(inpot)
		except EOFError:
			pass
		
		self.dump(f)
		quit()
	def dump(self,f):
		sett={"conffile":self.conffile,
			 "links":   self.links}
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
class Logger():
	def __init__(self,warn=False,verbose=False):
		self.v=verbose
		self.w=warn
	def debug(self,msg):
		if self.v:
			sprintn(msg)
	def warning(self,msg):
		if self.w or self.v:
			sprintn(msg)
	def error(self,msg):
		sprintn(msg)
def main(manmode=False,verbose=False,help=False,configure=False):
	global conf
	conf=Config()
	conf.load()
	if configure:
		conf.set_tings()
		quit()
	if help:
		print("--conf       Triggers configuration and quits after this.\n--help       Triggers help and quits.\n--overwrite  overwrites all previously downloaded files (WARNING: This may result in really long waiting and massive Data usage.)")
		quit()
	for arg in sys.argv:
		if "/watch?v=" in arg:
			with YDL(YDL_OPTS) as ydl:
				ydl.download([arg])
			manmode=True
		elif "/playlist?list=" in arg:
			playlist(arg)
			manmode=True
	if manmode:
		quit()
	try:
		with YDL(YDL_OPTS) as ydl:
			for link in conf.links:
				sprintn("LINK ",conf.links.index(link)+1)
				if "/watch?v=" in link:
					print(end="\033[s")
					ydl.download([conf.url])
				elif "/playlist?list=" in link:
					playlist(link,conf.files,ydl,verbose)
				else:
					raise ValueError("Invalid link type")
			sprintn("Finished")
	except Exception as e:
		print("Some major Error happened:",e)
	finally:
		print("\nDownloaded: "+str(conf.stats[True])+"\nExisting: "+str(conf.stats[None])+"\nFailed: "+str(conf.stats[False]))

if __name__=="__main__":
	if "--help" in sys.argv:
		help=True
	else:
		help=False
	if "--conf" in sys.argv:
		configure=True
	else:
		configure=False
	if "--verbose" in sys.argv or "-v" in sys.argv:
		verbose=True
		print("VERBOSE")
	else:
		verbose=False
	if "--warnings" in sys.argv:
		warn=True
	else:
		warn=False
	YDL_OPTS={"outtmpl":"%(title)s","format":"bestaudio/best","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"opus","preferredquality":"320"}],"postprocessor_args":{"-metadata":"comment='hi'"},"progress_hooks":[singvidhook],"logger":Logger(warn,verbose)}
	main(help=help,configure=configure,verbose=verbose)
