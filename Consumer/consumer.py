import logging
from logging.config import dictConfig
import os
from mykafka import MyKafka
from influxDB import *
import sensors_schema
import sys

WORKORDER = 'workorder'
METRICS = 'metrics'


class Consumer(object):
    """
      A class used to represent Kafka Consumer

      ...

      Attributes
      ----------
      kafka_brokers : str
          the ip address and the port of Kafka server
      stream_type : str
          the type of the stream (it could be either metrics or workoder)
      topic_name : str
          the name of kafka topic to publish the data to
      database_name : int
          the name of the influxDB
     host_name : int
          the ip address of the influx server
     port : int
          the port ofthe influx server
     influx_batch_size : int
          the size of the chunk to be inserted in the influx

      Methods
      -------
      init_db(None)
          initialize the connection to the influxdb
      measurement_formulate(None)
          Structure the measurement to fit with the influxDB format.
      run(None)
          Start consuming messages from Kafka topic and storing them in influxDB
        """
    def __init__(self):
        '''
        initialize the different parameters and the connection to Kafka server.
        '''
        if 'KAFKA_BROKERS' in os.environ:
            self.kafka_brokers = os.environ['KAFKA_BROKERS'].split(',')
        else:
            raise ValueError('KAFKA_BROKERS environment variable not set')

        if 'STREAM_TYPE' in os.environ:
            self.stream_type = os.environ['STREAM_TYPE']
        else:
            raise ValueError('STREAM_TYPE environment variable not set')

        if 'KAFKA_TOPIC' in os.environ:
            self.topic_name = os.environ['KAFKA_TOPIC']
        else:
            raise ValueError('KAFKA_TOPIC environment variable not set')

        if 'DATABASE_NAME' in os.environ:
            self.database_name = os.environ['DATABASE_NAME']
        else:
            raise ValueError('DATABASE_NAME environment variable not set')

        if 'INFLUX_IP' in os.environ:
            self.host_name = os.environ['INFLUX_IP']
        else:
            raise ValueError('INFLUX_IP environment variable not set')

        if 'INFLUX_PORT' in os.environ:
            self.port = int(os.environ['INFLUX_PORT'])
        else:
            raise ValueError('INFLUX_PORT environment variable not set')
        if 'INFLUX_BATCH_SIZE' in os.environ:
            self.influx_batch_size = int(os.environ['INFLUX_BATCH_SIZE'])
        else:
            raise ValueError('INFLUX_BATCH_SIZE environment variable not set')
        # self.database_name = "firas_db"
        # self.host_name = '192.168.0.7'
        # self.port = 8086
        # self.kafka_brokers = "192.168.0.7:49154"
        # self.topic_name = 'new_topic_workorder'
        # self.stream_type = 'workorder'
        # self.influx_batch_size = 10
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
        self.logger.info("Initializing Kafka Consumer")
        self.logger.info("KAFKA_BROKERS={0}".format(self.kafka_brokers))
        # Connect to Kafka
        self.mykafka = MyKafka(self.kafka_brokers, self.topic_name)

    def init_db(self):
        '''
        Initialize the connection to InfluxDB
        :return:
        '''
        self.database = InfluxBD(database_name=self.database_name,
                                 host_name=self.host_name,
                                 port=self.port,
                                 batch_size=self.influx_batch_size)
        self.logger.info("InfluxDB Initialized")

    @staticmethod
    def measurement_formulate(measure, stream_type):
        '''
        Re-structure the observations to fit in InfluxDB
        '''
        if stream_type == WORKORDER:
            measurement = Measurement(measurement=stream_type,
                                      tags={'product': measure['product']},
                                      time=measure['time'],
                                      fields={'production': float(measure['production'])}
                                      )
        elif stream_type == METRICS:
            measurement = Measurement(measurement=stream_type,
                                      tags={'id': measure['id']},
                                      time=measure['time'],
                                      fields={'val': float(measure['val'])}
                                      )

        return measurement

    def run(self):
        '''
        Start consuming messages from Kafka topic and storing them in influxDB
        :return: None
        '''
        self.init_db()
        try:
            for message in self.mykafka.consumer:
                self.logger.info("Consumed data from Kafka")
                # print(message.value)
                sensors_schemas = {WORKORDER: sensors_schema.work_order_schema,
                                   METRICS: sensors_schema.metric_schema
                                   }
                data = Measurement.validate_measurements(message.value, sensors_schemas[self.stream_type])
                measurements = [self.measurement_formulate(m, self.stream_type).data_point() for m in data]
                self.database.store_measurement(measurements)
                self.logger.info("Successfully store in database")
        except KeyboardInterrupt:
            sys.exit()


if __name__ == "__main__":
    logging.info("Initializing Stream Stats Polling")
    main = Consumer()
    main.run()
