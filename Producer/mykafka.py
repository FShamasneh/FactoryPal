from kafka import KafkaProducer
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

             Methods
             -------
             send_chunk_data(json_data)
                 the endpoint that connects the producer to the kafka message broker and used to send the chunks
                 received from the REST API
             """
    def __init__(self, kafka_brokers, topic_name):
        self.topic_name = topic_name
        self.producer = KafkaProducer(
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            bootstrap_servers=kafka_brokers
        )

    def send_chunk_data(self, json_data):
        '''
        sends data to Kafka message broker
        :param json_data:
        :return:
        '''
        self.producer.send(self.topic_name, json_data)
