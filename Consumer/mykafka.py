from kafka import KafkaConsumer
import json


class MyKafka(object):
    """
                 A class used to represent the connection to the Kafka message broker
                 ...

                 Attributes
                 ----------
                 kafka_brokers : str
                     the ip of the kafka message broker and the port
                topic_name: str
                     the name of the kafka topic
                 """
    def __init__(self, kafka_brokers, topic_name):
        self.topic_name = topic_name
        self.consumer = KafkaConsumer(topic_name,
                                      bootstrap_servers=kafka_brokers,
                                      auto_offset_reset='earliest'
                                      )

