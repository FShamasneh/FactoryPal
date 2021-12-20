## Prerequisite
- A virtual machine (VM) that runs docker and docker compose. 
- Install Java on the VM (It will be used by NiFi)
- Install python on the VM (It will be used by one of the NiFi processors)
- Clone the Repository

## Installations 

### Kafka message broker 
- `cd YOUR PATH/FactoryPal/infrastructure/kafka-docker`
- `docker-compose up`

### InfluxDB message broker 
- `cd YOUR PATH/FactoryPal/infrastructure/influx_grafana`
- `docker-compose up`

### HTTP Streamer 
- `cd YOUR PATH/FactoryPal/HTTPDataStreamer`
- Modify the `.env` with the IP address of your host vm and the desired port number for the HTTP API. 
- `docker-compose up`

### Consumer 
- `cd YOUR PATH/FactoryPal/Consumer`
- Modify the `.env`  to:
	KAFKA_BROKERS='YOUR_VM_IP_ADDRESS:KAFKA_PORT' 
	KAFKA_TOPIC_METRICS=topic_metrics_new 
	KAFKA_TOPIC_WORKORDER=topic_workorder_new 
	STREAM_TYPE_WORKORDER='workorder'
	STREAM_TYPE_METRICS='metrics'
	DATABASE_NAME='firas_db'
	INFLUX_IP='YOUR_VM_IP_ADDRESS'
	INFLUX_PORT=8086
	INFLUX_BATCH_SIZE=10
- `docker-compose up`

### Producer 
- `cd YOUR PATH/FactoryPal/Producer`
- Modify the `.env`  to:
   API_URL_WORKORDER='http://YOUR_VM_IP_ADDRESS:HTTP_APT_PORT/workorder'
	API_URL_METRICS='http://YOUR_VM_IP_ADDRESS:HTTP_APT_PORT/metrics'
	KAFKA_BROKERS='YOUR_VM_IP_ADDRESS:KAFKA_PORT'
	KAFKA_TOPIC_METRICS=topic_metrics_new
	KAFKA_TOPIC_WORKORDER=topic_workorder_new
	SLEEP=0.1
	
- `docker-compose up`


### NiFi 
The containerized version of NiFi is not stable without using an orchestrator, so we have to do the manual installation (The file size is around 1.5GB). Please follow the steps:
1. wget https://dlcdn.apache.org/nifi/1.15.1/nifi-1.15.1-bin.tar.gz
2. `sudo tar -xvzf nifi-1.15.1-bin.tar.gz`
3. `sudo ./nifi.sh start`
4. check nifi status using `sudo ./nifi.sh start`
5. try `vm_ip_address:8080/nifi` (it should works fine)
6. `cd YOUR_PATH/nifi-1.15.0`
7. `mkdir local_scripts docs`
8. `cd local_scripts`
9. add this file`YOUR_PATH/FactoryPal/NiFi/NiFiProcessors/analyzer.py` to `local_scripts` directory
10. make it executable, use: `chmod +x analyzer.py`
11. The template in the following directory should be imported into NiFi to get the entire data pipeline `YOUR_PATH/FactoryPal/NiFi/template`
12. The `GetGroupedProducts-InfluxDBQuery` && `GetGroupedMetrics-InfluxDBQuery` should be reconfigured to work with the new config of InfluxDB. (Please take a look at the figure bellow)
![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/4.png)
13. Modify the path in `ProcessStream-GenerateReport` processor to the new path of `analyzer.py` script. 
![alt text](https://github.com/FShamasneh/FactoryPal/blob/main/images/8.png)
14. Run NiFi and check the `docs` directory to see the generated report.
