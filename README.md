# status-to-elastic
Python script that records nodes' status and metrics.

* The script runs as an infinite loop, with sleep intervals defined in the config file.
* Each interval, the script iterates over the existing nodes, parses some metrics from the corresponding json files and writes them to Elastic Search index, in order to be later visualized.

### Run instructions:
1. Install required packages from requirements.txt
2. Run the py script, with the conf file in the same dir.
