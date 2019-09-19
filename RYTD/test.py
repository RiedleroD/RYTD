#!/usr/bin/env python3

import socket

SERVER = "localhost"
PORT = 10000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

while True:
  out_data = input(">>> ")
  client.sendall(bytes(out_data, "UTF-8"))
  in_data = client.recv(1024).decode()
  if out_data == "bye" or out_data=="" or in_data == "bye":
    break
  print(in_data)

client.close()
