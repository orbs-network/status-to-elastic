import configparser
import logging
import traceback
from logging.handlers import TimedRotatingFileHandler
from time import sleep

import requests

logger = logging.getLogger("nodes_monitor")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler("nodes_monitor.log", when="d", interval=1, backupCount=5)
logger.addHandler(handler)

DISKS_NAMES = {'/': 'root', '/mnt/data': 'mount'}  # TODO: support nodes with different mapping

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('nodes_monitor.conf')
    while True:
        try:
            status = requests.get(config['urls']['nodes_status']).json()
            committee_nodes = status['CommitteeNodes']
            for node_address, params in committee_nodes.items():
                try:
                    ip = params["Ip"]
                    eth_writer = config['urls']['eth_writer'].format(ip)
                    data = requests.get(eth_writer).json()
                    eth_balance = data['Payload']['EtherBalance']

                    metrics = {"name": params['Name'], 'eth_balance': int(eth_balance)/10**18}

                    boyar_status = config['urls']['boyar_status'].format(ip)
                    data = requests.get(boyar_status).json()
                    for disk in data['Payload']['Metrics']['Disks']:
                        if name := DISKS_NAMES.get(disk['Mountpoint']):
                            metrics.update({f'{name}_total_mbytes': disk['TotalMbytes'],
                                            f'{name}_used_mbytes': disk['UsedMbytes'],
                                            f'{name}_used_pct': disk['UsedPercent']})

                    logger.info(metrics)
                    requests.post(config['urls']['es_index'], json=metrics)
                    logger.debug(f"Inserted metrics for node {ip}")
                except:
                    print(f"Failed to gather metrics for node {node_address}")
                    traceback.print_exc()
        except:
            traceback.print_exc()
        finally:
            sleep(config.getint('params', 'sleep_cycle'))
