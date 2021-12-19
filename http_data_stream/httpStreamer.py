#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask
import os
import logging
from logging.config import dictConfig


class HttpStreamer(object):
    """
          A class used as a simulator for an API, it gets the data from local files (under [data] directory)
          and send a chunk of specific size back as a response for an HTTP GET request. Please note, that the files
          names are used to create dynamic routes. For example, if we have a file called metrics.json in the data folder
          it will be used to create an url called (http://192.168.0.4:5000/metrics)

          ...

          Attributes
          ----------
          file_counters : dict
              A counter dictionary that tracks the current reading offset of the different files
          batched_data : dict
              A dictionary that contains all the files as keys and a list of their values as a list of chunks.
          total_len : dict
              the total number of chunks per file
          host_ip : str
              The ip address of the host of the API
          port : str
              The port number of the host of the API
          batch_size : str
              the size of the batch that used to divide the stream from specific file

          Methods
          -------
          init_offsets_counter(None)
              initialize the offsets of the different data sources with zeros.
          get_file_names(None)
              Get all the file names from the "data" directory
          get_data_from_files(None)
              read the data from each file separately
          batchs_per_stream(stream_data, chunk_size)
              it will divide the stream into batches based on the size of the batch
          stream_batching(batch_size)
              it adds all the chunks in a dictionary based on for all the files
          run(None)
              it will run the flask app
          """

    def __init__(self):
        self.file_counters = {}
        self.batched_data = {}
        self.total_len = {}

        if 'HTTP_SERVER_IP' in os.environ:
            self.host_ip = os.environ['HTTP_SERVER_IP']
        else:
            raise ValueError('HTTP_SERVER_IP environment variable not set')
        if 'HTTP_SERVER_PORT' in os.environ:
            self.port = int(os.environ['HTTP_SERVER_PORT'])
        else:
            raise ValueError('HTTP_SERVER_PORT environment variable not set')
        if 'BATCH_SIZE' in os.environ:
            self.batch_size = int(os.environ['BATCH_SIZE'])
        else:
            raise ValueError('BATCH_SIZE environment variable not set')

        # self.host_ip = '192.168.0.4'
        # self.port = '5000'
        # self.batch_size = 10

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
        self.logger.info("Initializing HTTP Streamer")

        # initialize counters to point to the current data offset
        self.init_offsets_counter()
        # get the data baches from local files
        self.stream_batching(self.batch_size)

    def init_offsets_counter(self):
        '''
        Initiate all the reading offsets for the different streams
        :return: None
        '''
        for file in self.get_file_names():
            self.file_counters[file] = 0

    @staticmethod
    def get_file_names():
        '''
        get a list of all filenames from "data" directory
        :return: list of filenames
        '''
        return os.listdir('data')

    @staticmethod
    def get_data_from_files(filename):
        '''
        read the data from a specific file
        :param filename: the name of the file
        :return: a dictionary of the read data
        '''
        filename = 'data/' + filename
        with open(filename) as jsonfile:
            return json.load(jsonfile)

    def batchs_per_stream(self, stream_data, chunk_size):
        '''
        divide a specific stream into batches based on the chunk size
        :param stream_data: the input data stream
        :param chunk_size: the size of the chunk
        :return: a stream divided into batches
        '''
        return [stream_data[x:x + chunk_size] for x in range(0, len(stream_data), chunk_size)]

    def stream_batching(self, batch_size):
        '''
        it will loop over all the streams in the "data" directory, and divide each stream into batches based on
        the batch/chunk size
        :param batch_size: the size of the batch
        :return: None
        '''
        for file in self.get_file_names():
            batches = self.batchs_per_stream(self.get_data_from_files(file), batch_size)
            self.total_len[file] = len(batches)
            self.batched_data[file] = batches

    def run(self):
        '''
        This function will run the flask API. It has dynamic routing based on the filenames in the "data" directory
        :return: None
        '''
        app = Flask(__name__)

        @app.route('/<filename>')
        def stream(filename):
            filename = filename + '.json'
            self.logger.info(f'{filename} - Chunk {self.file_counters[filename]} / {self.total_len[filename]}')
            if self.total_len[filename] == self.file_counters[filename]:
                return None
            response = json.dumps(self.batched_data[filename][self.file_counters[filename]])
            self.file_counters[filename] += 1
            return response

        @app.route('/')
        def index():
            return 'The path should be the IP address of the sever followed by the filename ex. http://[SERVER_IP]/[' \
                   'FILE_NAME] --> http://192.168.0.4/metrics '

        app.run(host=self.host_ip, port=self.port)


if __name__ == "__main__":
    logging.info("Initializing HTTP Streamer")
    main = HttpStreamer()
    main.run()
