#!usr/bin/python3
import sys
if __name__=="__main__":
	global curprocs
	curprocs=[]
	if "--help" in sys.argv or "-h" in sys.argv or "?" in sys.argv:
		print("""HELP

	--configure | -c | ¢ | Triggers configuration and quits after this.
	--help      | -h | ? | Triggers help and quits.
	--overwrite | -o | ø | Overwrites all previously downloaded files (WARNING: This may result in really long waiting and massive Data usage.)
	--directory	| -d | ð | Overrides the standard download directory with the path specified in the next argument.
	--warnings  | -w | ! | Prints ocurring warnings.
	--verbose   | -v | … | Verbose.""")
		quit()
	if "--configure" in sys.argv or "-c" in sys.argv or "¢" in sys.argv:
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
	if "--directory" in sys.argv:
		custom_dir=sys.argv[sys.argv.index("--directory")+1]
	elif "-d" in sys.argv:
		custom_dir=sys.argv[sys.argv.index("-d")+1]
		print("Switched to custom directory \"",custom_dir,"\"",sep="")
	elif "ð" in sys.argv:
		custom_dir=sys.argv[sys.argv.index("ð")+1]
	else:
		custom_dir=None
	if verbose:
		print("IMPORTING MODULES")
import pytube, os, io, mutagen, json,time
from base64 import b64encode
from youtube_dl import YoutubeDL as YDL
import urllib.request as urlreq
from urllib.parse import unquote as urlunquote
import subprocess as supro
from traceback import TracebackException as TBException
from psutil import disk_partitions

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

if verbose:
	print("DEFINING FUNCTIONS AND CLASSES")

def sprint(*s:str,sep:str="",end:str="",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)
def sprintn(*s:str,sep:str="",end:str="\n\r",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)
def sprintr(*s:str,sep:str="",end:str="\r",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)
def sprints(*s:str,sep:str="",end:str="\r",flush:bool=True):
	print(*s,sep=sep,end=end,flush=flush)

def safename(s:str):
	return s.replace("\"","'").replace("|","\u2223").replace(":","\u0589").replace("*","\u033d").replace("?","\uff1f").replace("/","\u2215").replace("\\","\uFF3C").replace("<","‹").replace(">","›")

def get_base64image(link:str):
	img=b64encode(urlreq.urlopen(link).read())
	if len(img)<=128:
		return img
	else:
		raise Exception("Image is too big")

def progrbar(percent):
	percent=round(percent/2,1)
	chrs=(""," ","▏","▎","▍","▌","▋","▊","▉","█")
	end=chrs[round((percent%1)*10)]
	amount=int(percent)
	if end!="":
		return "▕"+"█"*amount+end+" "*(49-amount)+"▏"
	else:
		return "▕"+"█"*amount+" "*(50-amount)+"▏"

def direct(link:str,files,path:str=None,verbose:bool=False):
	if path==None:
		path=conf.homedir
	fname=os.path.basename(urlunquote(link))
	if (not os.path.splitext(fname)[0] in conf.files.values()) or ("--overwrite" in sys.argv):
		print("Downloading: %s"%(fname))
		f=urlreq.urlopen(link)
		fpath=os.path.join(path,fname)
		with open(fpath,"wb") as download:
			download.write(f.read())
		print("→%s"%(fpath))
	else:
		print("Exists: %s"%(fname))

_hookdata={}

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
	#all of this is very inconsistent, sometimes the values are there, sometimes not.
	for key,value in d.items():
		_hookdata[key]=value
	stat=d["status"]
	try:
		elapsed=round(d['elapsed'],2)
	except KeyError:
		elapsed=""
	if stat=="downloading":
		try:
			eta=d['eta']
		except KeyError:
			eta=""
		try:
			percent=d["downloaded_bytes"]/d["total_bytes"]*100
		except KeyError:
			try:
				percent=d["downloaded_bytes"]/_hookdata["total_bytes"]*100
			except KeyError:
				percent=0
				sprint("\033[s\033[46m[Downloading]\033[0m ",eta," ","?"*50,end="\033[u")
				return
		sprint("\033[s\033[46m[Downloading]\033[0m ",eta," ",progrbar(percent),end="    \033[u")
	elif stat=="finished":
		sprintn("\033[42m[Finished]\033[0m ",elapsed,"  ")
		conf.stats[True]+=1
		try:
			del _hookdata["total_bytes"]
		except KeyError:
			pass
	else:
		sprint("HOLY F A NEW STATUS JUST GOT RECOGNIZED:",stat,end="\n\033[s")

def playlist(link,files,ydl,path,verbose=False):
	global curprocs
	sprintr("Checking...")
	links=pytube.Playlist("https://youtube.com/playlist?list="+link).parse_links()
	if verbose:
		sprintn(links)
	for link in links:
		i=link.split("watch?v=")[-1]
		if verbose:
			sprintn("\n\033[44m",links.index(link)+1,"/",len(links),"\033[49m\n\033[43mhttps://youtu.be/",i,"\033[49m ")
		else:
			sprint(links.index(link)+1,"/",len(links),": https://youtu.be/",i," : \033[7m[Checking...]\033[27m\033[13D")
		if (not i in conf.files) or ("--overwrite" in sys.argv):
			for proc in curprocs:
				procstate=proc.poll()
				if procstate==0:
					conf.stats[True]+=1
					if verbose:
						sprintn("\033[42mConversion Succeeded\033[0m")
					del proc
				elif procstate!=None:
					conf.stats[False]+=1
					if verbose:
						sprintn("\033[41mConversion Failed\033[0m")
					del proc
			if os.path.exists(os.path.join(conf.curdir,"RYTD_TMP")):
				try:
					os.remove(os.path.join(conf.curdir,"RYTD_TMP"))
				except OSError:
					if verbose:
						sprintn("\033[41mFailed to delete temp file (",os.path.join(conf.curdir,"RYTD_TMP"),")\033[0m")
			try:
				 info_dict=ydl.extract_info(os.path.join("https://youtu.be",i))
			except KeyboardInterrupt:
				conf.stats[False]+=1
				raise KeyboardInterrupt()
			except Exception as e:
				tbe=TBException.from_exception(e)
				sprintn("\033[41m[",tbe.exc_type.__name__,"]\033[0m ",tbe._str)
			else:
				command=[
					"ffmpeg","-v","0","-i","RYTD_TMP_"+info_dict["id"],"-vn","-y",
					"-metadata","copyright="+str(info_dict["license"]),
					"-metadata","comment="+str(info_dict["description"]),
					"-metadata","rytdid="+info_dict["id"],
					"-metadata","title="+info_dict["title"]]
				if info_dict["average_rating"]!=None:
					command+=["-metadata","rating="+str(int(info_dict["average_rating"])*20)]
				if info_dict["dislike_count"]!=None:
					command+=["-metadata","dislikes="+str(int(info_dict["dislike_count"])*20)]
				if info_dict["like_count"]!=None:
					command+=["-metadata","likes="+str(int(info_dict["like_count"])*20)]
				if info_dict["view_count"]!=None:
					command+=["-metadata","views="+str(int(info_dict["view_count"])*20)]
				try:
					thumbnail=get_base64image(info_dict["thumbnail"])
				except Exception as e:
					if verbose:
						tbe=TBException.from_exception(e)
						print("\033[41mCouldn't get thumbnail:",tbe.exc_type.__name__,"-",tbe._str)
				else:
					command+=["-metadata",b"metadata_block_picture="+thumbnail]
				if info_dict["creator"]!=None:
					command+=["-metadata","artist="+str(info_dict["creator"])]
				else:
					command+=["-metadata","artist="+info_dict["uploader"]]
				command.append(os.path.join(path,safename(info_dict["title"])+".opus"))
				if verbose:
					sprint("[")
					sprint(*command,sep=",")
					sprintn("]")
				curprocs.append(supro.Popen(command,stdin=supro.PIPE))
				if verbose:
					sprintn()
		else:
			if verbose:
				sprintn("\033[7m[Exists]\033[0m")
			else:
				sprint("\033[s\033[7m[Exists]\033[27m",end="     \n\r")
			conf.stats[None]+=1

class Config():
	def __init__(self,custom_dir):
		self.os=os.name
		if custom_dir==None:
			self.curdir=os.path.abspath(os.path.dirname(__file__))
		else:
			self.curdir=os.path.abspath(os.path.dirname(custom_dir))
		os.chdir(self.curdir)
		self.links=[]
		self.files={}
		self.conffile=os.path.abspath(os.path.join(self.curdir,".rytdconf"))
		self.stats={True:0,None:0,False:0}
	def load(self):
		status=self.load_from_file(self.curdir)
		self.load_files()
		self.dump()
	def load_files(self):
		for playlist in self.links:
			for dirpath, dirnames, filenames in os.walk(playlist.path):
				for f in filenames:
					name=os.path.splitext(f)[0]
					fpath=os.path.join(dirpath,f)
					try:
						muf=mutagen.File(fpath)
					except:
						sprintn("Corrupt file: %s"%(fpath))
						continue
					if muf==None:
						continue
					try:
						i=muf["rytdid"]
						if i!=None:
							i=i[0]
						else:
							raise KeyError()
					except KeyError:
						try:
							i=muf["comment"]
							if i!=None:
								i=i[0]
							else:
								pass
						except KeyError:
							pass
					if i==None:
						possible=[char for char in string.ascii_letters+string.digits+"_-äöüÄÖÜß"]
						while i in self.files.keys():
							i="".join([random.choice(possible) for i in range(8)])
					self.files[i]=name
						
	def load_from_file(self,path):
		try:
			conffile=open(os.path.abspath(os.path.join(self.curdir,".rytdconf")),"r")
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
		sprintn("""
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
				path=os.path.abspath(argument)
				if os.path.isdir(path):
					path=os.path.join(path,"default.rpl")
				elif path.endswith(".rpl"):
					path=os.path.abspath(path)
				else:
					path=os.path.abspath(path+".rpl")
				try:
					f=open(path,"w+")
				except OSError:
					sprintn("Something about the path is wrong! (",path,")")
				else:
					try:
						f.write("{}")
					except OSError:
						sprintn("Couldn't write to file.")
					
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
			except KeyboardInterrupt:
				print("DONT FUCKING DO THAT, IT'S VERY FUCKING FUCK FOR THE CONFIG FILE")
				try:
					json.dump(links,plfile)
				except KeyboardInterrupt:
					print("ok then. It's potentially corrupted now.\nI won't help you, you are fucking stupid.")
					quit()
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

def main(warn=False,verbose=False,configure=False,custom_dir=None):
	global conf
	if verbose:
		sprintr("Loading Settings...")
	conf=Config(custom_dir)
	conf.load()
	if verbose:
		sprintn("Loaded Settings    ")
	if configure:
		conf.set_tings()
		quit()
	YDL_OPTS={"outtmpl":"","format":"bestaudio/best","progress_hooks":[singvidhook],"logger":Logger(warn,verbose),"call_home":True}
	try:
		for pl in conf.links:
			sprintn(conf.links.index(pl)+1,"/",len(conf.links),":\033[47m\033[30m",pl.f,"\033[0m")
			for link in pl:
				if link.typ=="yt":
					YDL_OPTS["outtmpl"]=os.path.join(pl.path,"%(title)s.%(ext)s")
					sprintn(pl.index(link)+1,"/",len(pl),":\033[35mVIDEO\033[0m")
					with YDL(YDL_OPTS) as ydl:
						ydl.download([os.path.join("https://youtu.be",link.link)])
				elif link.typ=="xx":
					YDL_OPTS["outtmpl"]=os.path.join(pl.path,"%(title)s.%(ext)s")
					sprintn(pl.index(link)+1,"/",len(pl),":\033[34mEXTERN\033[0m")
					with YDL(YDL_OPTS) as ydl:
						ydl.download([link.link])
				elif link.typ=="pl":
					YDL_OPTS["outtmpl"]="RYTD_TMP_%(id)s"
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
		x=0
		for proc in curprocs:
			x+=1
			l=len(curprocs)
			sprintr("Waiting for subprocess ",x,"/",l)
			try:
				proc.wait()
			except KeyboardInterrupt:
				proc.terminate()
			try:
				proc.wait(timeout=1)
			except supr.TimeoutExpired:
				proc.kill()
			if proc.poll()==0:
				conf.stats[True]+=1
				if verbose:
					sprintn("\033[42mConversion ",x,"/",l," Succeeded\033[0m   ")
			else:
				conf.stats[False]+=1
				if verbose:
					sprintn("\033[41mConversion ",x,"/",l," Failed with exit code ",proc.poll(),"\033[0m")
		for dirpath, dirnames, filenames in os.walk(conf.curdir):
			for f in filenames:
				if f.startswith("RYTD_TMP_"):
					try:
						os.remove(os.path.join(dirpath,f))
					except Exception as e:	
						sprintn("\033[41mFailed to remove File '",f,"', because of an Error: ",e,"\033[0m")
					else:
						if verbose:
							sprintn("\033[42mSuccessfully removed File ",f,"\033[0m")
		sprintn("\nDownloaded: ",conf.stats[True],"\nExisting: ",conf.stats[None],"\nFailed: ",conf.stats[False])

if __name__=="__main__":
	main(configure=configure,verbose=verbose,warn=warn,custom_dir=custom_dir)

