## HTTPDataStreamer 

An API was implemented to simulate different streams. It takes the stream as a JSON input file. The file should be stored under **“data”** directory. The API will generate dynamic routes based on the file name. The size of the returned response could be set via *BATCH_SIZE* variable in *.env* file in HTTPDataStreamer directory. The IP address of the host and the port number should be specified in the *.env* file. The following figure shows the GET response of the API for the two streams stored under the **“data”** directory. 

![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/1.jpg?raw=true)
![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/2.jpg?raw=true)

The  HTTPDataStreamer was implemented as a micro-service and deployed inside a docker container. 

## Kafka producer

The Kafka producer will get the data from the API. Each producer will handle a single stream, and this stream will be published in Kafka topic. The name of the topic should be specified as an environment variable for the script. This variable can be set via the *.env* file under **“Producer”** directory. Many other parameters need to be specified in the *.env* file before building up the image, These variables are the URL of the API, the IP of Kafka message broker, and the SLEEP variable to control the speed of data ingestion. The Kafka producer was also implemented as a micro-service and deployed inside a docker container. Using the docker compose file two producers can start at the same time to read from different streams simultaneously. The *.env* file has been used a centralized configuration file to configure all the producers. 

## Kafka Consumer
The Kafka consumer will consume the data from a specific Kafka topic specified as a system variable in the *.env* file under **“Consumer”** directory. The consumer will persist the data by writing it to a time series database called *InfluxDB*. Each consumer will persist the data for a single stream in a specific InfluxDB series stored in a shared database between all consumers. 
The Kafka consumer was also implemented as a micro-service and deployed inside a docker container. Using the docker compose file two consumers can start at the same time to store the data from two different streams  into an InfluxDB. The *.env* file has been used a centralized configuration file to configure all the consumers. 
The following figure shows a producer (shown on the upper left) that gets metrics stream from an API. And a consumer (shown on the bottom left) that consumes metrics stream and store it to InfluxDB (shown on the upper right). 
![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/3.jpg?raw=true)

## NiFi