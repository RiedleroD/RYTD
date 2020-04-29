import socket, sys, os

class Communicator():
	def __init__(self):
		self.SERVER="rasphi.serveblog.net"
		self.PORT=10000
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	def connect(self):
		self.client.connect((self.SERVER, self.PORT))
	def send_raw(self,data:str):
		self.client.sendall(bytes(data,"UTF-8"))
	def search(self,urls:list
	def read(self):
		return self.client.recv(1024).decode()

if __name__ == '__main__':
    pass

