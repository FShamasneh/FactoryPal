import requests
import json

SUCCESS_RESPONSE = 200


class Stream(object):
    """
         A class used to represent the connection with the REST API

         ...

         Attributes
         ----------
         stream_api_url : str
             the url to connect to the REST API

         Methods
         -------
         get_data(None)
             To get data from the API
         get_chunk_data(None)
             load the obtained data into JSON file
         """
    def __init__(self, api_url):
        self.stream_api_url = api_url

    def get_data(self):
        '''
        receive GET response from a rest API
        :return:
        '''
        response = requests.get(self.stream_api_url)
        if response.status_code == SUCCESS_RESPONSE:
            return response.text
        return None

    def get_chunk_data(self):
        '''
        load the received chunks into JSON
        :return:
        '''
        data = self.get_data()
        if data:
            return json.loads(data)
        return None
