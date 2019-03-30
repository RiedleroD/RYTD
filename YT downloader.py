import pytube, os, sys, io
curdir=os.path.abspath(os.path.dirname(__file__))
def singvid(link):
	link=link.split("&")[0]
	print(link)
	yt=Vid(link)
	streams=yt.streams
	print("All streams:\n"+str(streams.all()))
	astreams=streams.filter(type="audio")
	print("Audio streams:\n"+str(astreams.all()))
	astream=astreams.first()
	print("Selected stream:\n"+str(astream))
	try:
		astream.download(output_path=curpos)
	except AttributeError as e:
		if not astreams.all()==[]:
			raise e
	if astreams.all()==[]:
		raise Exception("Could not download it because no audio streams were found")
	sys.stdout.write("Finished"+" "*50+"\r")
class Vid(pytube.YouTube):
	def ineed(self):
		self.name=self.title
		self.i=self.video_id
def stuff(vid):
	vid.ineed()
	sys.stdout.write("\033[s"+strip(vid.title)[0])
	sys.stdout.flush()
	if (not vid.i in files) or ("--overwrite" in sys.argv):
		try:	
			vid.streams.filter(type="audio").first().download(output_path=curdir,filename=strip(vid.title,vid.i))
		except Exception as e:
			if e is KeyboardInterrupt:
				quit()
			else:
				print(" \033[7m\033[31m[Failed]\033[0m",e,end=" "*10+"\n\r")
				stats[False]+=1
		else:
			sys.stdout.write(" \033[7m\033[32m[Finished]\033[0m\n\r")
			stats[True]+=1
	else:
		sys.stdout.write(" \033[7m[Exists]\033[27m\n\r")
		stats[None]+=1
	sys.stdout.flush()
def playlist(link,files):
	global stats
	#https://www.youtube.com/playlist?list=PLk5KkYG8je9DsAgKQcRrT9wOlTHiJmORl
	stats={True:0,None:0,False:0}
	sys.stdout.write("Checking...\r")
	links=pytube.Playlist(link).parse_links()
	for link in links:
		i=link.split("?v=")[-1]
		sys.stdout.write(str(links.index(link)+1)+"/"+str(len(links))+": youtube.com"+link+": \033[7m[Checking...]\033[27m\033[13D")
		sys.stdout.flush()
		if i in files:
			sys.stdout.write("\033[s\033[7m[Exists]\033[27m     \n\r")
			stats[None]+=1
			continue
		sys.stdout.flush()
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
				sys.stdout.write("\033[7m\033[31m[Failed]\033[0m"+" "*10+"\n\r")
			else:
				stuff(vid)
		else:
			stuff(vid)
	sys.stdout.write("Finished\n")
	sys.stdout.flush()
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
		else:
			while i in files:
				i+=1
		return s,i
	else:
		return str(i)+"\u2020"+s
files={}
for dirpath, dirnames, filenames in os.walk(curdir):
	for f in filenames:
		name,i=strip(os.path.splitext(f)[0])
		files[i]=name
link=input("Link please. (Single video or full playlist)\n")
if "/watch?v=" in link:
	singvid(link)
elif "/playlist?list=" in link:
	try:
		playlist(link,files)
	except KeyboardInterrupt:
		pass
	finally:
		print("\nDownloaded: "+str(stats[True])+"\nExisting: "+str(stats[None])+"\nFailed: "+str(stats[False]))
else:
	raise ValueError("Invalid link type")
