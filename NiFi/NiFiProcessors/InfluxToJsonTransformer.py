import json
import sys
import traceback
from java.nio.charset import StandardCharsets
from org.apache.commons.io import IOUtils
from org.apache.nifi.processor.io import StreamCallback
from org.python.core.util import StringUtil


class TransformCallback(StreamCallback):
    def __init__(self):
        pass

    def process(self, inputStream, outputStream):
        """It will take NiFI influxdb data input stream and  transform it to JSON per key

         Parameters
         ----------
         inputStream : str
             The main stream received from NiFi
        outputStream: str
            The output will be encapsulated in the outputStream

         Returns
         -------
         Dict
            a dictionary for each key : [Values...]
         """
        try:
            # Read input FlowFile content
            input_text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
            input_obj = json.loads(input_text)
            # Transform content
            output_obj = self.influx_extractor(input_obj)
            # Write output content
            output_text = json.dumps(output_obj)
            outputStream.write(StringUtil.toBytes(output_text))

        except:
            traceback.print_exc(file=sys.stdout)
            raise

    def influx_extractor(self, input_stream):
        """This function will perform the actual transformation of the influxRecordQuery NiFI processor output
           and transform it to JSON per keys

              Parameters
              ----------
              inputStream : dict
                  The main stream received from NiFi

              Returns
              -------
              Dict
                 a dictionary for each key : [Values...]
              """
        base_arr = input_stream['results'][0]['series']
        numOfGroups = len(base_arr)
        key_name = list(base_arr[0]['tags'].keys())[0]
        group_names = [base_arr[i]['tags'][list(base_arr[0]['tags'].keys())[0]] for i in range(0, numOfGroups)]
        grouped_keys = {dict[group_names[i]]: base_arr[i]['values'] for i in range(0, numOfGroups)}

        return grouped_keys[key_name]


flowFile = session.get()
if flowFile != None:
    flowFile = session.write(flowFile, TransformCallback())

# Finish by transferring the FlowFile to an output relationship
session.transfer(flowFile, REL_SUCCESS)
