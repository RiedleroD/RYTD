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
	#'downloaded_bytes':	int<downloaded bytes>
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
		print(stat,d['_eta_str'],end="\033[u",flush=True)
	elif stat=="finished":
		print(stat,d['_elapsed_str'],end="\n",flush=True)
	else:
		print("HOLY F A NEW STATUS JUST GOT RECOGNIZED:",stat,end="\n\033[s",flush=True)
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
				 info_dict=ydl.extract_info("https://youtube.com"+link)
			except KeyboardInterrupt:
				raise KeyboardInterrupt()
				conf.stats[False]+=1
			except:
				pass
			else:
				command="ffmpeg -v 0 -i '"+conf.curdir+"/RYTD_TMP' -vn -y -metadata comment='"+info_dict["id"]+"' '"+conf.homedir+"/"+info_dict["title"]+".opus'"
				os.system(command)
				os.remove(conf.curdir+"/RYTD_TMP")
				conf.stats[True]+=1
		else:
			if verbose:
				sprintn("\033[7m[Exists]\033[0m")
			else:
				sprint("\033[s\033[7m[Exists]\033[27m",end="     \n\r")
			conf.stats[None]+=1
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
		for dirpath, dirnames, filenames in os.walk(self.homedir):
			for f in filenames:
				name=os.path.splitext(f)[0]
				i=0
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
		try:
			conffile=open(self.curdir+"/.rytdconf","r")
		except OSError:
			self.set_tings()
		else:
			try:
				sett=json.load(conffile)
			except json.decoder.JSONDecodeError:
				raise ValueError("Corrupt Config File. (hint: it's json, get it together.)")
			else:
				for link in sett["links"]:
					self.links.append(link)
				self.homedir=sett["homedir"]
			finally:
				conffile.close()
	def set_tings(self):
		f=self.curdir+"/.rytdconf"
		inpot=""
		while not inpot in ("EOF","\"EOF\""):
			inpot=input("Paste one Link at a time in here, and finish the input with \"EOF\". If you want to delete all existing links, type \"RESET\".\n")
			if not inpot in ("EOF","\"EOF\""):
				if inpot in ("RESET","\"RESET\""):
					self.links=[]
					print("Resetted")
				else:
					self.links.append(inpot)
					if random.randrange(0,200)==69:
						print("okay...\n...go ahead...")
		inpot=input("Specify ")
		self.dump(f)
		quit()
	def dump(self,f):
		sett={"conffile":self.conffile,
			 "links":   self.links,
			 "homedir": self.homedir}
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
		command="ffmpeg -v 0 -i \""+dirpath+"/"+i+"\u2020"+f+ext+"\" -vn -y -metadata comment=\""+i+"\" \""+dirpath+"/"+f+".opus\""
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
	YDL_OPTS={"outtmpl":"RYTD_TMP","format":"bestaudio/best","progress_hooks":[singvidhook],"logger":Logger(warn,verbose)}#,"postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"opus","preferredquality":"320"}],"postprocessor_args":["-metadata comment='hi'"]}
	main(help=help,configure=configure,verbose=verbose)
