# -*-coding:Utf-8 -*

from common import *

import socket, pickle
import enum
import sys
import threading
import random
import time

# local 에서 테스트 하기 위해 랜덤 포트 넘버로 지정.
data_port = random.randint(33000, 60000)
my_addr = ("localhost", data_port)

# publisher의 경우 관리하는 리스트
match_list = []


# keep alive message 를 처리하는 스레드 함수
def getKeepAliveMsg(conn,topic):
	global my_addr

	ok_msg = "ok"
	fail_msg = "fail"

	while True:

		raw_msg = conn.recv(1024)
		msg = pickle.loads(raw_msg)
		print("keep alive message : topic ", str(msg.topic_name))
		if topic.topic_name == msg.topic_name:
			print("keep alive ok")
			conn.send(ok_msg.encode('utf-8'))

		else:
			print("keep alive error")
			conn.send(fail_msg.encode('utf-8'))
			break


# publisher 가 match report 를 받았을 때 실행시키는 스레드 함수
def sendSubRegRequest(addr, topic, file_path):

	print("try send register request to subscriber ", str(addr[1]))

	time.sleep(0.5)
	data_string = pickle.dumps(topic)

	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(addr)

		while True:
			s.send(data_string)

			msg = s.recv(1024).decode('utf-8')
			print (msg)

			if msg != "ok":
				print("register request error")
			else:
				break

		print("now sending file")
		file = open(file_path,'rb')
		time.sleep(0.5)

		l = file.read(1024)
		while l:
			s.send(l)
			l = file.read(1024)
		s.close()
		file.close()
		print("file transfer finish")

		if topic.data_period == 0:
			break

		# data period 만큼 쉰 후 데이터 재전송
		time.sleep(topic.data_period)


def pub_mode(file_path):

	global data_port, my_addr, broker_addr, match_list

	topic_name = input("Topic name > ")
	data_period = int(input("Data period (0 if you want to send just once) > "))

	topic = Topic(TopicType.PUBLISH, topic_name, my_addr, data_period)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(broker_addr)

	data_string = pickle.dumps(topic)
	s.send(data_string)
	print ("finish send")

	msg = s.recv(1024).decode('utf-8')
	print (msg)

	if msg != "ok":
		print("topic register error")
		return

	# topic 등록이 끝났다면 match report 를 기다린다.
	# 연결되어 있는 소켓으로는 keep alive manage 합니다. 
	keep_alive_messager = threading.Thread(target = getKeepAliveMsg, args = (s, topic,))
	keep_alive_messager.start()

	listen_s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_s.bind(my_addr)
	print("bind success")

	while True:

		listen_s.listen()
		print("listen success")
		conn, _ = listen_s.accept()

		match = conn.recv(128)
		match_addr = pickle.loads(match)
		print("get matched with", str(match_addr[1]))
		match_list.append(match_addr)

		sub_reg_requester = threading.Thread(target = sendSubRegRequest, args = (match_addr, topic, file_path))
		sub_reg_requester.start()

		conn.close()


def sub_mode(file_path):

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

	if msg != "ok":
		print("topic register error")
		return

	# subscribe mode 는 topic register 가 끝나면 pub으로부터의 connect 을 기다려야함. 
	# 연결되어 있는 소켓으로는 keep alive manage 합니다. 
	keep_alive_messager = threading.Thread(target = getKeepAliveMsg, args = (s, topic,))
	keep_alive_messager.start()

	ok_msg = "ok"
	fail_msg = "fail"

	listen_s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_s.bind(my_addr)

	while True:

		listen_s.listen(1)
		print("listening...")
		conn, _ = listen_s.accept()

		req_data = conn.recv(1024)
		if len(req_data) == 0:
			continue 
		req_var = pickle.loads(req_data)
		print("register request from publisher arrived")
		print(req_var.topic_name)

		if req_var.topic_name == topic.topic_name:
			conn.send(ok_msg.encode('utf-8'))

		else:
			conn.send(fail_msg.encode('utf-8'))
			continue

		# 이제 파일 데이터가 오기를 기다립니다.
		print("waiting for file data")
		file = open(file_path,'wb')
		
		l = conn.recv(1024)
		while l:
			file.write(l)
			l = conn.recv(1024)

		conn.close()
		print("file arrived")


if __name__ == "__main__":

	mode = 0

	while mode!= 1 and mode!= 2:

		mode = int(input("1. Publisher, 2. Subscriber: "))
		if mode == 1:
			pub_mode(sys.argv[1])

		elif mode == 2:
			sub_mode(sys.argv[1])

		else:
			print("wrong input\n")

