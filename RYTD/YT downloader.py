#!/usr/bin/python3
import os,sys,json
import requests
import mutagen
import youtube_dl

if "-v" in sys.argv or "--verbose" in sys.argv:
	vprint=print
	def tprint(*args,**kwargs):	#terse; meaning: not verbose
		return
else:
	def vprint(*args,**kwargs):
		return
	tprint=print

curpath=os.path.abspath(os.path.dirname(__file__))
muspath=os.path.join(curpath,os.path.pardir)

class JbinC():
	"""You insert jsonbin.io id, you get a dictionary generator back"""
	def __init__(self,id:str="5de278ffb77d632ccda51790"):
		self.id=id
		self.url="https://api.jsonbin.io/b/%s/latest"%(self.id)
		self.content={}
	def read(self)->dict:
		if self.content=={}:
			self.content=requests.get(self.url)
			self.content=json.loads(self.content.text)
		return self.content
	def __call__(self,i,typ):
		for j,urls in self.items():
			if i==urls[typ]:
				return j
	def __contains__(self,*args,**kwargs):
		return self.read().__contains__(*args,**kwargs)
	def __delitem__(self,*args,**kwargs):
		return self.read().__delitem__(*args,**kwargs)
	def __eq__(self,*args,**kwargs):
		return self.read().__eq__(*args,**kwargs)
	def __ge__(self,*args,**kwargs):
		return self.read().__ge__(*args,**kwargs)
	def __getitem__(self,*args,**kwargs):
		return self.read().__getitem__(*args,**kwargs)
	def __gt__(self,*args,**kwargs):
		return self.read().__gt__(*args,**kwargs)
	def __iter__(self,*args,**kwargs):
		return self.read().__iter__(*args,**kwargs)
	def __le__(self,*args,**kwargs):
		return self.read().__le__(*args,**kwargs)
	def __len__(self,*args,**kwargs):
		return self.read().__len__(*args,**kwargs)
	def __lt__(self,*args,**kwargs):
		return self.read().__lt__(*args,**kwargs)
	def __ne__(self,*args,**kwargs):
		return self.read().__ne__(*args,**kwargs)
	def __repr__(self,*args,**kwargs):
		return self.read().__repr__(*args,**kwargs)
	def __setitem__(self,*args,**kwargs):
		return self.read().__setitem__(*args,**kwargs)
	def __sizeof__(self,*args,**kwargs):
		return self.read().__sizeof__(*args,**kwargs)
	def __ge__(self,*args,**kwargs):
		return self.read().__ge__(*args,**kwargs)
	def clear(self,*args,**kwargs):
		return self.read().clear(*args,**kwargs)
	def copy(self,*args,**kwargs):
		return self.read().copy(*args,**kwargs)
	def get(self,*args,**kwargs):
		return self.read().get(*args,**kwargs)
	def items(self,*args,**kwargs):
		return self.read().items(*args,**kwargs)
	def keys(self,*args,**kwargs):
		return self.read().keys(*args,**kwargs)
	def pop(self,*args,**kwargs):
		return self.read().pop(*args,**kwargs)
	def popitem(self,*args,**kwargs):
		return self.read().popitem(*args,**kwargs)
	def setdefault(self,*args,**kwargs):
		return self.read().setdefault(*args,**kwargs)
	def update(self,*args,**kwargs):
		return self.read().update(*args,**kwargs)
	def values(self,*args,**kwargs):
		return self.read().values(*args,**kwargs)

class File():
	def __init__(self,fpath:str,id:str,title:str=None):
		self.fpath=os.path.abspath(fpath)
		self.fname=os.path.basename(self.fpath)
		self.name,self.ext=os.path.splitext(self.fname)
		self.path=os.path.dirname(self.fpath)
		self.id=id
		if title==None:
			self.title=self.name
		else:
			self.title=title

class FileFinder():
	"""Finds files that were downloaded by RYTD."""
	def __init__(self):
		self.searchfiles()
	def append(self,f:File):
		assert type(f)==File,"argument f has to be instance of File"
		self.files.append(f)
	def __getitem__(self,index:(str,int)):
		if type(index)==str:
			result=[f for f in self.files if f.id==index]
			if result==[]:
				raise KeyError(index)
			else:
				return result[0]
		elif type(index)==int:
			return self.files[index]
	def searchfiles(self):
		self.files=[]
		for dirpath,dirnames,filenames in os.walk(muspath):
			for f in filenames:
				filepath=os.path.join(dirpath,f)
				try:
					file=mutagen.File(filepath)
				except mutagen.MutagenError:
					print("\033[31mFound corrupt file: %s\033[0m"%filepath)
				if file==None:
					continue
				else:
					tags=dict(file.tags)
					try:
						title=tags["title"][0]
					except (KeyError,IndexError):
						title=None
					try:
						self.files.append(File(filepath,tags["rytdid"][0],title))
					except KeyError:
						pass
		vprint("Found Files:",*["%s:  %s"%(i,fpath) for i,fpath in enumerate(self.filepaths())],sep="\n")
	def filenames(self):
		return [f.fname for f in self.files]
	def filepaths(self):
		return [f.fpath for f in self.files]
	def files(self):
		return [*self.files]
	def __iter__(self):
		return iter(self.files)

class Downloader():
	def __init__(self):
		self.ff=FileFinder()
		self.jbinc=JbinC()
		self.set_default_opts()
	def set_default_opts(self):
		self.opts={
			'format':"bestaudio/best",
			'postprocessors':[{'key':"FFmpegExtractAudio",'preferredcodec':conf.codec}],
			'logger':Logger(),
			'progress_hooks':[self.progrhook]}
	def progrhook(self,d:dict):
		print(d)

class Logger():
	debug=vprint
	warning=vprint
	error=print

class Config():
	def __init__(self):
		self.data={}
		self.paths=[]
		self.load()
	def load(self,fpath:str=os.path.join(curpath,".rytdconf")):
		fpath=os.path.abspath(fpath)
		with open(fpath) as f:
			self.data.update(json.load(f))
			vprint("Loaded config file: %s"%(fpath))
		if not os.path.samefile(self.conffile,fpath):
			self.load(self.data.conffile)
		self.paths.append(fpath)
	def __getattr__(self,index:str):
		try:
			return self.__dict__[index]
		except KeyError:
			return self.data[index]

conf=Config()
down=Downloader()

