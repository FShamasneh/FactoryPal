# Data Engineer Challenge

How you implement the challenge is up to you. The only requirement is code must run with minimal setup on our own machines.

1. Create an ingestion system for two data streams. It must accept HTTP messages. Example files are provided for both streams. The first stream named 'metrics.json' is an example of machine data. The second, 'workorder.json', defines what product ran when and how much output was produced. Persist this data.

2. Create an ETL pipeline that reads the data from step 1, and finds the top three parameters that correlate to the production output of each product, and output them in a static report.

Document any design considerations and how to run your code. You may use the provided files to test but your entire system will be tested on a different set of files.
