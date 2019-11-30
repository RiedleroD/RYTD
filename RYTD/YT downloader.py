#!/usr/bin/python3
import os,sys,json
import requests

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
