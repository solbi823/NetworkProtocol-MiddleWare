# -*-coding:Utf-8 -*

from common import *

import socket, pickle
import enum
import sys
import threading

sub_list = []
pub_list = []
new_match = []		# match buffer : (pub addr, sub_addr)

def alarmToPub(match):

	global match_list

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
	sock.close()

	# find match
	if topic_type == TopicType.PUBLISH:

		pub_list.append(data_var)

		tmp_sub_list = []
		for sub in sub_list:
			if sub.topic_name == data_var.topic_name:
				new_match.append((data_var.addr, sub.addr))
			else:
				tmp_sub_list.append(sub)

		sub_list = tmp_sub_list

		print("pub list #: ", str(len(pub_list)))
		print("match #: ", str(len(new_match)))

	else:

		flag = False
		for pub in pub_list:
			if pub.topic_name == data_var.topic_name:
				new_match.append((pub.addr, data_var.addr))
				flag = True
				break
				
		if flag == False:
			sub_list.append(data_var)
			print("waiting sub list #: ", str(len(sub_list)))

		else:
			print("find matching one")

	# alarm to matched publishers
	print(len(new_match))
	for match in new_match:
		alarmer = threading.Thread(target = alarmToPub, args = (match, ))
		alarmer.start()



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

