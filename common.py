# -*-coding:Utf-8 -*

import enum

host = "127.0.0.1"
port = 36007
broker_addr = (host, port)

class Format:
	def __init__(self, file_name, file_size, value):
		self.file_name = file_name
		self.file_size = file_size
		self.value = value

class TopicType(enum.Enum):
	PUBLISH = 0
	SUBSCRIBE = 1
	EXPIRED = 2

class Topic:
	def __init__(self, topic_type, topic_name, addr, data_period = None):
		self.topic_type = topic_type
		self.topic_name = topic_name
		self.data_period = -1 if data_period is None else data_period
		# subscriber 일때는 -1

		self.addr = addr

