## HTTPDataStreamer 

An API was implemented to simulate different streams. It takes the stream as a JSON input file. The file should be stored under **“data”** directory. The API will generate dynamic routes based on the file name. The size of the returned response could be set via BATCH_SIZE variable in *.env* file in HTTPDataStreamer directory. The IP address of the host and the port number should be specified in the *.env* file. The following figure shows the GET response of the API for the two streams stored under the **“data”** directory. 

![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/1.png)
![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/2.png)

The  HTTPDataStreamer was implemented as a micro-service and deployed inside a docker container. 

## Kafka producer

The Kafka producer will get the data from the API. Each producer will handle a single stream, and this stream will be published in Kafka topic. The name of the topic should be specified as an environment variable for the script. This variable can be set via the *.env* file under **“Producer”** directory. Many other parameters need to be specified in the *.env* file before building up the image, These variables are the URL of the API, the IP of Kafka message broker, and the SLEEP variable to control the speed of data ingestion. The Kafka producer was also implemented as a micro-service and deployed inside a docker container. Using the docker-compose file two producers can start at the same time to read from different streams simultaneously. The *.env* file has been used as a centralized configuration file to configure all the producers. 

## Kafka Consumer

The Kafka consumer will consume the data from a specific Kafka topic specified as a system variable in the *.env* file under **“Consumer”** directory. The consumer will persist the data by writing it to a time-series database called *InfluxDB*. Each consumer will persist the data for a single stream in a specific InfluxDB series stored in a shared database between all consumers. 
The Kafka consumer was also implemented as a micro-service and deployed inside a docker container. Using the docker-compose file two consumers can start at the same time to store the data from two different streams into an InfluxDB. The *.env* file has been used as a centralized configuration file to configure all the consumers. 
The following figure shows a producer (shown on the upper left) that gets metrics stream from an API. And a consumer (shown on the bottom left) that consumes metrics stream and store it to InfluxDB (shown on the upper right). 

![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/3.png)

## NiFi

NiFi was used as an ETL system to manage the dataflow and perform the required transformations and processing on the data to finally generate the required report. The following figure shows the whole data pipeline implemented by NiFi.

![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/4.png)

### GetGroupedProducts-InfluxDBQuery && GetGroupedMetrics-InfluxDBQuery

The first two processors are the “`GetGroupedProducts-InfluxDBQuery`” and “`GetGroupedMetrics-InfluxDBQuery`”. They are communicating directly with the *InfluxDB* and used to extract the data by issuing the following two queries on the database: `SELECT production FROM "work_order" GROUP BY product` (for *GetGroupedProducts-InfluxDBQuery*) and `SELECT val FROM "metrics" GROUP BY id` (for *GetGroupedMetrics-InfluxDBQuery*). The output of these two processors are a response in the following InfluxDB format: `{"results":[{"series":[{"name":"workorder","tags":{"product":"0"},"columns":["time","production"],"values":[[1.624378574E9,0.0],[1.624383671E9,15.685808348048699]]},{"name":"workorder","tags":{"product":"1"},"columns":["time","production"],"values":[[1.624378577E9,7.1646233636807],[1.624383524E9,13.122035182560696]]}]}]}`

The following figure shows the configuration of the processor in NiFi (both are the same, the only difference is the Influx query):

![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/5.png)



### TransformInfluxDBResponseToJSON

A jython script was written in this processor to transfer the output of the previous stage into JSON format. The jython script could be found under `(NiFi/NiFiProcessors/InfluxToJsonTransformer.py)`.
The output of this processor is: `{"product": {"0": [[1624378574.0, 0.0], [1624383671.0, 15.685808348048699]], "1": [[1624378577.0, 7.1646233636807], [1624383524.0, 13.122035182560696]]}}`. The configuration on this processor is shown bellow: 

![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/6.png)

### MergeProductsMetricsStreams

This processor is used to combine the transformed output of the two queries. The bin packing algorithm has been used for that purpose.  The output of this processor shown bellow: 
`{"product": {"0": [[1624378574.0, 0.0], [1624383671.0, 15.685808348048699]], "1": [[1624378577.0, 7.1646233636807], [1624383524.0, 13.122035182560696]]}}{"id": {"11": [[1624378434.0, 353.5568796864811], [1624383684.0, 353.9960632605844]], "12": [[1624379121.0, 96.82810842135835], [1624383763.0, 886.4294819342731]], "13": [[1624377912.0, 269.84823425570124], [1624383481.0, 270.18457392435494]], "14": [[1624378266.0, 549.8618514848156], [1624383957.0, 550.2662390244327]], "15": [[1624378551.0, 574.5044195900442], [1624378817.0, 574.446350307184]], "16": [[1624378704.0, 523.8905685094085], [1624383003.0, 571.0187880638839]], "17": [[1624378767.0, 51.71054983511379], [1624383673.0, 52.447006920032514]], "18": [[1624378184.0, 197.1934435520138], [1624378543.0, 197.16050399446962]], "19": [[1624377478.0, 797.3838872696809], [1624382745.0, 797.7017409855807]], "0": [[1624378736.0, 56.66657362779242], [1624378897.0, 1012.6612174390209]], "1": [[1624378233.0, 5314.289628209279], [1624378564.0, 7390.25765811748]], "2": [[1624379031.0, -334.14615446735354], [1624379460.0, 987.4464640066592]], "3": [[1624379762.0, 1855.6625749660134], [1624383791.0, -3039.4672564316743]], "4": [[1624378627.0, -9972.056046579735], [1624384245.0, 4014.3050428960887]], "5": [[1624383823.0, 746.5692463034409], [1624384014.0, 805.4995279403867]], "6": [[1624378866.0, 808.9163271900304], [1624379868.0, 1071.86246909526]], "7": [[1624378524.0, 608.1955629332933], [1624388684.0, 1073.9985843705258]], "8": [[1624378671.0, 597.7339093828783], [1624388964.0, 600.9932253057073]], "9": [[1624378670.0, 35.79146084847345], [1624393108.0, -122.80764599573486]], "10": [[1624378100.0, 553.1947969841733], [1624378937.0, 553.2030445186301]]}}`

The following figure shows the configuration for `MergeProductsMetricsStreams` processor:
![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/7.png)

### ProcessStream-GenerateReport

This processor is the most interesting one. It integrates a python script that runs locally on the machine. This python script could be found under `(NiFi/NiFiProcessors/analyzer.py)`. To find the correlation between the production output and the 20 metrics we have. A *standardization* has been applied on all the features to ensure that they are running on the same scale. The cross-correlation was used to find the correlation score between the production output for each product and the other metrics. An additional statistical summary report was generated based on the data. A sample output of this processor could be found under `(NiFi/SampleOfGeneratedReport/products_metrics-2021_12_18_21_17_19_184.txt)`.
The configuration of this processor is shown bellow: 
![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/8.png)

### UpdateReportName

This processor is used to change the name of stream, to a filename attached by the current running timestamp.

![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/9.png)

### StoreReportLocally

This processor is used to store the previously generated report on the local machine that hosts NiFi. 
The configuration of this processor is shown bellow: 
![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/10.png)
