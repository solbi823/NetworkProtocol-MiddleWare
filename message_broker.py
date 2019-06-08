# -*-coding:Utf-8 -*

from common import *

import socket, pickle
import enum
import sys
import threading
import time

sub_list = []
pub_list = []
new_match = []		# match buffer : (pub addr, sub_addr)


def alarmToPub(match):

	global new_match

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# connect to publisher
	print("get here")
	s.connect(match[0])
	print("connect success")

	# send match subscriber's address
	data_string = pickle.dumps(match[1])
	s.send(data_string)
	print ("sent match subscriber address")

	new_match.remove(match)

def recvTopicThread(sock):

	global sub_list, pub_list, new_match

	ok_msg = "ok"
	fail_msg = "fail"

	while True:
		data = sock.recv(1024)
		data_var = pickle.loads(data)
		topic_type = data_var.topic_type

		print(data_var.topic_type)
		print(data_var.topic_name)

		if topic_type == TopicType.PUBLISH or topic_type == TopicType.SUBSCRIBE:
			break

		else:
			print("wrong topic error")
			sock.send(fail_msg.encode('utf-8'))
			continue

	# send ok message to pub or sub
	sock.send(ok_msg.encode('utf-8'))


	# 새로 들어온 topic 으로 인해 생기는 match를 찾습니다. 
	if topic_type == TopicType.PUBLISH:

		pub_list.append(data_var)

		for sub in sub_list:
			if sub.topic_name == data_var.topic_name:
				new_match.append((data_var.addr, sub.addr))

		print("pub list #: ", str(len(pub_list)))
		print("match #: ", str(len(new_match)))

	else:

		sub_list.append(data_var)

		for pub in pub_list:
			if pub.topic_name == data_var.topic_name:
				new_match.append((pub.addr, data_var.addr))
				print("find matching one")
				break
				
		print("sub list #: ", str(len(sub_list)))


	# 매치된 publisher들에게 알려주는 스레드를 생성합니다. 
	print(len(new_match))
	for match in new_match:
		alarmer = threading.Thread(target = alarmToPub, args = (match, ))
		alarmer.start()

	# keep alive 관리
	sock.settimeout(3)
	while True:

		time.sleep(10)

		print("keep alive? sending topic...")
		sock.send(data)

		try:
			msg = sock.recv(1024).decode('utf-8')
		except socket.timeout:
			print("timeout. send fail.")
			break

		print(msg)
		if msg != "ok":
			break

	if topic_type == TopicType.PUBLISH:
		pub_list.remove(data_var)
	else:
		sub_list.remove(data_var)


if __name__ == "__main__":


	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		print("내 주소: ", str(broker_addr))
		s.bind(broker_addr)
		s.listen()

		while True:
			conn, addr = s.accept()
			print(str(addr), "에서 접속")
			topic_receiver = threading.Thread(target = recvTopicThread, args = (conn,))
			topic_receiver.start()

