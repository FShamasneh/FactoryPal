from stream import Stream
from mykafka import MyKafka
import logging
import time
from logging.config import dictConfig
import os



class Producer(object):
    """
      A class used to represent Kafka Producer

      ...

      Attributes
      ----------
      kafka_brokers : str
          the ip address and the port of Kafka server
      stream_url : str
          the url of the rest API
      topic_name : str
          the name of kafka topic to publish the data to
      sleep : int
          the duration to sleep between different chunks published to kafka

      Methods
      -------
      init_stream(None)
          initialize the connection to the REST API
      run(None)
          Ingest data from the REST API and publish it to Kafka topic
      """

    def __init__(self):
        """Initialize the Kafka producer parameters, and connect to Kafka message brocker

         Parameters
         ----------
            NONE

         Returns
         -------
            NONE
         """
        if 'KAFKA_BROKERS' in os.environ:
            self.kafka_brokers = os.environ['KAFKA_BROKERS'].split(',')
        else:
            raise ValueError('KAFKA_BROKERS environment variable not set')

        if 'API_URL' in os.environ:
            self.stream_url = os.environ['API_URL']
        else:
            raise ValueError('API_URL environment variable not set')

        if 'KAFKA_TOPIC' in os.environ:
            self.topic_name = os.environ['KAFKA_TOPIC']
        else:
            raise ValueError('KAFKA_TOPIC environment variable not set')

        if 'SLEEP' in os.environ:
            self.sleep = float(os.environ['SLEEP'])
        else:
            raise ValueError('SLEEP environment variable not set')

        logging_config = dict(
            version=1,
            formatters={
                'f': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
            },
            handlers={
                'h': {'class': 'logging.StreamHandler',
                      'formatter': 'f',
                      'level': logging.DEBUG}
            },
            root={
                'handlers': ['h'],
                'level': logging.DEBUG,
            },
        )

        self.logger = logging.getLogger()
        dictConfig(logging_config)
        self.logger.info("Initializing Kafka Producer")
        self.logger.info("KAFKA_BROKERS={0}".format(self.kafka_brokers))

        # Connect to Kafka message broker
        self.mykafka = MyKafka(self.kafka_brokers, self.topic_name)

    def init_stream(self):
        '''
        Initialize the REST API
        '''
        self.stream = Stream(self.stream_url)
        self.logger.info("Stream Stats Polling Initialized")

    def run(self):
        '''
        Ingest data from the REST API and publish it to Kafka topic
        '''
        self.init_stream()
        while True:
            data = self.stream.get_chunk_data()
            if data is not None:
                self.logger.info("Successfully polled Stream data")
                self.mykafka.send_chunk_data(data)
                self.logger.info("Published data to Kafka")
            time.sleep(self.sleep)


if __name__ == "__main__":
    logging.info("Initializing Stream Stats Polling")
    main = Producer()
    main.run()
