# -*-coding:Utf-8 -*

from common import *

import socket, pickle
import enum
import sys
import threading

data_port = 36007
my_addr = ("localhost", data_port)

class Match:
	def __init__(self, pub):
		self.pub = pub
		self.addr_list = []

	def add_addr(self, addr):
		self.addr_list.append(addr)

	def match_num(self):
		return len(self.addr_list)


match_list = []

def sendSubRegRequest(addr, topic):

	print("try send register request to subscriber ", str(addr[1]))
	data_port += 1
	my_addr = ("localhost", data_port)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(addr)
	data_string = pickle.dumps(topic)

	while True:
		s.send(data_string)

		msg = s.recv(1024).decode('utf-8')
		print (msg)

		if msg != "ok":
			print("topic register error")
			continue
		else:
			break

	print("now sending file")



def pub_mode(file_path):

	global data_port, my_addr, broker_addr, match_list

	topic_name = input("Topic name > ")
	data_period = int(input("Data period (0 if you want to send just once) > "))
	# 일단은 한번만 보내기
	data_period = 0

	topic = Topic(TopicType.PUBLISH, topic_name, my_addr, data_period)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(broker_addr)

	data_string = pickle.dumps(topic)
	s.send(data_string)
	print ("finish send")

	msg = s.recv(1024).decode('utf-8')
	print (msg)
	s.close()

	if msg != "ok":
		print("topic register error")
		return

	# topic 등록이 끝났다면 match report 를 기다린다. 
	data_port += 1
	my_addr = ("localhost", data_port)
	listen_s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_s.bind(my_addr)
	listen_s.listen(1)
	conn, _ = listen_s.accept()

	while True:
		match = conn.recv(1024)
		match_addr = pickle.loads(match)
		print("get matched")
		print(match_addr[1])
		match_list.append(match_addr)

		sub_reg_requester = threading.Thread(target = sendSubRegRequest, args = (match_addr, topic, ))
		sub_reg_requester.start()







def sub_mode():

	global data_port, my_addr, broker_addr

	topic_name = input("Topic name > ")

	topic = Topic(TopicType.SUBSCRIBE, topic_name, my_addr)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(broker_addr)

	data_string = pickle.dumps(topic)
	s.send(data_string)
	print ("finish send")

	msg = s.recv(1024).decode('utf-8')
	print (msg)
	s.close()

	if msg != "ok":
		print("topic register error")
		return

	# subscribe mode 는 topic register 가 끝나면 pub으로부터의 connect 을 기다려야함. 

	ok_msg = "ok"
	fail_msg = "fail"

	data_port += 1
	my_addr = ("localhost", data_port)

	listen_s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_s.bind(my_addr)
	listen_s.listen(1)
	conn, _ = listen_s.accept()

	while True:
		req_data = conn.recv(1024)
		req_var = pickle.loads(req_data)
		print("register request from publisher arrived")
		print(req_var.topic_name)

		if req_var.topic_name == topic.topic_name:
			conn.send(ok_msg.encode('utf-8'))
			break
		else:
			conn.send(fail_msg.encode('utf-8'))
			continue

	# 이제 파일 데이터가 오기를 기다립니다.
	print("waiting for file data")



if __name__ == "__main__":

	mode = 0

	while mode!= 1 and mode!= 2:

		mode = int(input("1. Publisher, 2. Subscriber: "))
		if mode == 1:
			pub_mode(sys.argv[1])

		elif mode == 2:
			sub_mode()

		else:
			print("wrong input\n")

