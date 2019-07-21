import pytube, os, sys, io, mutagen, json
from youtube_dl import YoutubeDL as YDL
import urllib.request as urlreq
from traceback import TracebackException as TBException
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

def bashsafe(s:str):
	s=s.replace("/","|")
	s=s.replace("\\","|")
	s=s.replace("\'","`")
	s=s.replace("\"","`")
	return s

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
	stat=d["status"]
	try:
		elapsed=round(d['elapsed'],2)
	except KeyError:
		elapsed=""
	try:
		eta=d['eta']
	except KeyError:
		eta=""
	if stat=="downloading":
		sprint("\033[46m[Downloading]\033[0m ",eta,"    ",end="\033[u")
	elif stat=="finished":
		sprint("\033[42m[Finished]\033[0m ",elapsed,end="   \n\033[46m[Converting]\033[0m\r")
		conf.stats[True]+=1
	else:
		print("HOLY F A NEW STATUS JUST GOT RECOGNIZED:",stat,end="\n\033[s",flush=True)

def playlist(link,files,ydl,path,verbose=False):
	sprintr("Checking...")
	links=pytube.Playlist("https://youtube.com/playlist?list="+link).parse_links()
	if verbose:
		sprintn(links)
	for link in links:
		i=link.split("watch?v=")[-1]
		if verbose:
			sprintn("\n\033[44m",links.index(link)+1,"/",len(links),"\033[49m\n\033[43m",i,"\033[49m ")
		else:
			sprint(links.index(link)+1,"/",len(links),": https://youtu.be/",i,": \033[7m[Checking...]\033[27m\033[13D")
		if (not i in conf.files) or ("--overwrite" in sys.argv):
			try:
				 info_dict=ydl.extract_info("https://youtube.com"+link)
			except KeyboardInterrupt:
				raise KeyboardInterrupt()
				conf.stats[False]+=1
			except Exception as e:
				tbe=TBException.from_exception(e)
				sprintn("\033[41m[",tbe.exc_type.__name__,"]\033[0m ",tbe._str)
			else:
				command="ffmpeg -v 0 -i '"+conf.curdir+"/RYTD_TMP' -vn -y -metadata comment='"+info_dict["id"]+"' '"+path+"/"+bashsafe(info_dict["title"])+".opus'"
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
		sprintr("Loading Settings...")
		status=self.load_from_file(self.curdir)
		self.load_files()
		sprintn("Loaded Settings    ")
		self.dump()
	def load_files(self):
		for playlist in self.links:
			for dirpath, dirnames, filenames in os.walk(playlist.path):
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
				for playlist in sett["playlists"]:
					self.load_from_playlist(playlist)
			finally:
				conffile.close()
	def load_from_playlist(self,path):
		try:
			plfile=open(path,"r")
		except OSError:
			sprintn("Couldn't load playlist: ",path)
		else:
			try:
				linkdict=json.load(plfile)
			except json.decoder.JSONDecodeError:
				raise ValueError("Corrupt Config File. (hint: it's json, get it together.)")
			else:
				links=[]
				for link,typ in linkdict.items():
					links.append(RLink(link,typ))
				self.links.append(RLinkArray(links,path))
			finally:
				plfile.close()
	def set_tings(self):
		inpot=""
		curpl=0
		print("""
Enter as many lines as you want like this:
[command] [argument]

Aviable commands:
	new
		creates a new playlist in the path specified after that
	add
		adds whatever comes after it to the currently selected playlist
	select
		selects the playlist in the specified path
	reset
		deletes all playlists
	end
		saves the configuration and exits
""")
		while not inpot.startswith("end"):
			if " " in inpot or "\t" in inpot:
				try:
					command,argument=inpot.split()
				except ValueError:
					sprintn("Couldn't get command and/or argument")
			else:
				command=inpot
			command=command.lower()
			
			if command=="reset":		#reset
				self.links=[]
				sprintn("Resetted")
			elif command=="new":		#new
				if argument.endswith("/"):
					path=argument+"default.rpl"
				elif argument.endswith(".rpl"):
					path=argument
				else:
					path=argument+".rpl"
				try:
					f=open(path,"w+")
				except OSError:
					sprintn("Something about the path is wrong! (",path,")")
				else:
					try:
						f.write("{}")
					except OSError:
						print("Couldn't write to file.")
					
			elif command=="":			#empty string
				pass
			elif command.startswith("["):#brackets
				sprintn("No, I meant without the brackets.")
			elif command=="add":		#add
				self.links[curpl].append()
				if random.randrange(0,200)==69:
					sprintn("okay...\n...go ahead...")
				sprintn("Added ",link," to ",self.links[curpl].path)
			else:						#unrecognizable
				sprintn("Invalid command:",inpot)
			inpot=input("")
		self.dump()
		quit()
	def dump(self):
		sprintr("Dumping Settings...")
		playlists={}
		for playlist in self.links:
			links={}
			for link in playlist:
				links[link.link]=link.typ
			playlists[playlist.f]=links
			
		sett={"conffile":self.conffile,
			 "playlists":list(playlists)}
		conffile=open(self.conffile,"w+")
		try:
			json.dump(sett,conffile)
		finally:
			conffile.close()
		for f, links in playlists.items():
			plfile=open(f,"w+")
			try:
				json.dump(links,plfile)
			finally:
				plfile.close()
		sprintn("Dumped settings    ")

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

class RLinkArray(list):
	def __init__(self,links:"list of RLink",path:str):
		self.links=links
		self.path=os.path.dirname(path)
		self.f=path
	def __iter__(self):
		return self.links.__iter__()
	def append(self,*args):
		return self.links.append(*args)
	def sort(self,*args,**kwargs):
		return self.links.sort(*args,**kwargs)
	def pop(self,*args,**kwargs):
		return self.links.pop(*args,**kwargs)
	def clear(self,*args,**kwargs):
		return self.links.clear(*args,**kwargs)
	def copy(self,*args,**kwargs):
		return self.links.copy(*args,**kwargs)
	def count(self,*args,**kwargs):
		return self.links.count(*args,**kwargs)
	def extend(self,*args,**kwargs):
		return self.links.extend(*args,**kwargs)
	def index(self,*args,**kwargs):
		return self.links.index(*args,**kwargs)
	def insert(self,*args,**kwargs):
		return self.links.insert(*args,**kwargs)
	def remove(self,*args,**kwargs):
		return self.links.remove(*args,**kwargs)
	def reverse(self,*args,**kwargs):
		return self.links.reverse(*args,**kwargs)
	def __len__(self,*args,**kwargs):
		return self.links.__len__(*args,**kwargs)

def main(manmode=False,warn=False,verbose=False,configure=False):
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
	YDL_OPTS={"outtmpl":"","format":"bestaudio/best","progress_hooks":[singvidhook],"logger":Logger(warn,verbose)}
	try:
		for pl in conf.links:
			sprintn(conf.links.index(pl)+1,"/",len(conf.links),":\033[47m\033[30m",pl.f,"\033[0m")
			for link in pl:
				if link.typ=="yt":
					YDL_OPTS["outtmpl"]=pl.path+"%(title).%(ext)"
					with YDL(YDL_OPTS) as ydl:
						sprintn(pl.index(link)+1,"/",len(pl),":\033[35mVIDEO\033[0m")
						ydl.download(["https://youtu.be/"+link.link])
				elif link.typ=="xx":
					YDL_OPTS["outtmpl"]=pl.path+"%(title).%(ext)"
					with YDL(YDL_OPTS) as ydl:
						sprintn(pl.index(link)+1,"/",len(pl),":\033[34mEXTERN\033[0m")
						ydl.download([link.link])
				elif link.typ=="pl":
					YDL_OPTS["outtmpl"]="RYTD_TMP"
					sprintn(pl.index(link)+1,"/",len(pl),":\033[36mPLAYLIST\033[0m")
					with YDL(YDL_OPTS) as ydl:
						playlist(link.link,conf.files,ydl,pl.path,verbose)
				elif link.typ=="dt":
					sprintn(pl.index(link)+1,"/",len(pl),":\033[37mDIRECT\033[0m")
					direct(link.link,conf.files,pl.path,verbose)
				else:
					raise ValueError("Invalid link type")
			sprintn("Finished")
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
	main(configure=configure,verbose=verbose,warn=warn)

