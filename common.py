# -*-coding:Utf-8 -*

import enum

host = "localhost"
port = 36007
broker_addr = (host, port)

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

