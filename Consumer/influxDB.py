from influxdb import InfluxDBClient
from json import loads
from jsonschema import Draft4Validator


class Measurement:
    """
     A class used to formulate the measurement in the correct formate for InfluxDB
     ...

     Attributes
     ----------
     measurement : str
         the name of the InfluxDB Series
     tags: str
         The id of the different measurements
     time: str
         The timestamp of each observation
     fields: str
         The actual numerical values of the observations

     Methods
     -------
     data_point(None)
         formulate the measurements in the influxDB format as dictionaries
    validate_measurements(values, schema)
         validate the measurements against specific schema before inserting into InfluxDB.
         """
    def __init__(self, measurement, tags, time, fields):
        self.measurement = measurement
        self.tags = tags
        self.time = time
        self.fields = fields

    def data_point(self):
        return {
            "measurement": self.measurement,
            "tags": self.tags,
            "time": self.time,
            "fields": self.fields
        }

    @staticmethod
    def validate_measurements(values, schema):
        '''
        validate the measurements before inserting into InfluxDB
        :param values:
        :param schema:
        :return: data_json
        '''
        processed_values = values.decode()
        data_json = loads(processed_values)
        validator = Draft4Validator(schema)
        for msg in data_json:
            for error in validator.iter_errors(msg):
                print(error, end='\n-----------------------\n')
        return data_json


class InfluxBD:
    """
     A class used to establish the connection with InfluxDB
     ...

     Attributes
     ----------
     database_name : str
         the name of the database
     host_name: str
         the IP address of the InfluxDB server
     port: str
         the port to connect to InfluxDB
     batch_size: str
         the number of observations to insert in InfluxDB as a chunk (default. 10)

     Methods
     -------
     store_measurement(None)
         Store the measurements in the influxDB
    """
    def __init__(self, database_name, host_name='localhost', port=8086, batch_size=10):
        try:
            self.client = InfluxDBClient(host=host_name, port=port)
            self.client.create_database(database_name)
            self.client.switch_database(database_name)
            self.batch_size = batch_size
        except self.client.InfluxDBClientError as e:
            print(f'{e}\nCould not connect to database: {database_name}')

    def store_measurement(self, value):
        self.client.write_points(value, batch_size=self.batch_size)
