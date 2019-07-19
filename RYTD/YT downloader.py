import pytube, os, sys, io, mutagen, json
from youtube_dl import YoutubeDL as YDL
import urllib.request as urlreq
#
#POSSIBLE ARGS:
#	--conf
#		triggers configuration and then quits
#	--help
#		shows help
#	--overwrite
#		download and convert videos even if existent.
#	<link>
#		a link.
#
def sprint(*s:str,sep:str="",end:str="",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)
def sprintn(*s:str,sep:str="",end:str="\n\r",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)
def sprintr(*s:str,sep:str="",end:str="\r",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)

def direct(link,files,verbose=False):
	fname=link.split("/")[-1]
	if not fname in conf.files.values():
		f=urlreq.urlopen(link)
		with open(conf.homedir+"/"+fname,"wb") as download:
			download.write(f.read())

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
	if stat=="downloading":
		print(d['status'],d['_eta_str'],end="\033[u",flush=True)
	elif stat=="finished":
		print(d['status'],d['_elapsed_str'],end="\n",flush=True)
		conf.stats[True]+=1
	else:
		print("HOLY F A NEW STATUS JUST GOT RECOGNIZED:",stat,end="\n\033[s",flush=True)

def playlist(link,files,ydl,verbose=False):
	if verbose:
		sprintn("Checking...")
	else:
		sprintr("Checking...")
	links=pytube.Playlist("https://youtube.com/playlist?list="+link).parse_links()
	if verbose:
		sprintn(links)
	for link in links:
		i=link.split("watch?v=")[-1]
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
				for link,typ in sett["links"].items():
					self.links.append(RLink(link,typ))
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
		links={}
		for link in self.links:
			links[link.link]=link.typ
		sett={"conffile":self.conffile,
			 "links":   links,
			 "homedir": self.homedir}
		conffile=open(f,"w+")
		try:
			json.dump(sett,conffile)
		finally:
			conffile.close()

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

class RLink():
	def __init__(self,link:str,typ:str):
		self.link=link
		self.typ=typ	#pl for youtube playlist, yt for youtube video, dt for direct file link, xx for everything else

def main(manmode=False,verbose=False,configure=False):
	global conf
	conf=Config()
	conf.load()
	if configure:
		conf.set_tings()
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
				if link.typ=="yt":
					ydl.download(["https://youtu.be/"+link.link])
				elif link.typ=="xx":
					ydl.download([link.link])
				elif link.typ=="pl":
					playlist(link.link,conf.files,ydl,verbose)
				elif link.typ=="dt":
					direct(link.link,conf.files,verbose)
				else:
					raise ValueError("Invalid link type")
			sprintn("Finished")
	except Exception as e:
		print("Some major Error happened:",e)
	finally:
		print("\nDownloaded: "+str(conf.stats[True])+"\nExisting: "+str(conf.stats[None])+"\nFailed: "+str(conf.stats[False]))

if __name__=="__main__":
	if "--help" in sys.argv or "-h" in sys.argv or "?" in sys.argv:
		print("""HELP

--configure | -c |   | Triggers configuration and quits after this.
--help      | -h | ? | Triggers help and quits.
--overwrite | -o |   | Overwrites all previously downloaded files (WARNING: This may result in really long waiting and massive Data usage.)
--warnings  | -w | ! | Prints ocurring warnings.
--verbose   | -v | … | Verbose.""")
		quit()
	if "--configure" in sys.argv or "-c" in sys.argv:
		configure=True
		print("CONFIGURE")
	else:
		configure=False
	if "--verbose" in sys.argv or "-v" in sys.argv or "…" in sys.argv:
		verbose=True
		print("VERBOSE")
	else:
		verbose=False
	if "--warnings" in sys.argv or "-w" in sys.argv or "!" in sys.argv:
		warn=True
	else:
		warn=False
	YDL_OPTS={"outtmpl":"RYTD_TMP","format":"bestaudio/best","progress_hooks":[singvidhook],"logger":Logger(warn,verbose)}
	main(configure=configure,verbose=verbose)
