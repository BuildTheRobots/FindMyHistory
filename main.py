import argparse
import time
import os
import curses
from datetime import datetime
from tabulate import tabulate
from lib.constants import JSON_LAYER_SEPARATOR
from lib.constants import FINDMY_FILES
from lib.constants import NAME_SEPARATOR
from lib.constants import JSON_LAYER_SEPARATOR
from lib.constants import NULL_STR
from lib.constants import TIME_FORMAT
from lib.constants import DATE_FORMAT
from lib.log_manager import LogManager


def parse_args():
    parser = argparse.ArgumentParser(
        description='Record Apple findmy history for Apple devices.')
    parser.add_argument(
        '--refresh',
        type=int,
        action='store',
        default=100,
        help='Refresh interval (ms).')
    parser.add_argument(
        '--name_keys',
        type=str,
        action='append',
        default=['name', 'deviceDiscoveryId', 'serialNumber'],
        help='Keys used to construct the filename for each device.')
    parser.add_argument(
        '--store_keys',
        type=str,
        action='append',
        default=['name', 'batteryLevel', 'batteryStatus', 'batteryLevel',
                 f'location{JSON_LAYER_SEPARATOR}timeStamp',
                 f'location{JSON_LAYER_SEPARATOR}latitude',
                 f'location{JSON_LAYER_SEPARATOR}longitude',
                 f'location{JSON_LAYER_SEPARATOR}verticalAccuracy',
                 f'location{JSON_LAYER_SEPARATOR}horizontalAccuracy',
                 f'location{JSON_LAYER_SEPARATOR}altitude',
                 f'location{JSON_LAYER_SEPARATOR}positionType',
                 f'location{JSON_LAYER_SEPARATOR}floorLevel',
                 f'location{JSON_LAYER_SEPARATOR}isInaccurate',
                 f'location{JSON_LAYER_SEPARATOR}isOld',
                 f'location{JSON_LAYER_SEPARATOR}locationFinished',
                 'id', 'deviceDiscoveryId', 'baUUID', 'serialNumber',
                 'identifier', 'prsId',
                 'deviceModel', 'modelDisplayName', 'deviceDisplayName'],
        help='Keys to log.')
    parser.add_argument(
        '--timestamp_key',
        type=str,
        action='store',
        default=f'location{JSON_LAYER_SEPARATOR}timeStamp',
        help='The key of timestamp in findmy JSON')
    parser.add_argument(
        '--log_folder',
        type=str,
        action='store',
        default='log',
        help='The path of log folder.')
    parser.add_argument(
        '--no_date_folder',
        action='store_true',
        help='By default, the logs of each day will be saved in a separated '
             'folder. Use this option to turn it off.')
    parser.add_argument(
        '--mqtt_broker_ip',
        type=str,
        action='store',
        help='The IP address of the MQTT broker.')
    parser.add_argument(
        '--mqtt_broker_port',
        type=int,
        action='store',
        default=1883,
        help='The port of the MQTT broker.')
    parser.add_argument(
        '--mqtt_broker_username',
        type=str,
        action='store',
        help='The username of the MQTT broker.')
    parser.add_argument(
        '--mqtt_broker_password',
        type=str,
        action='store',
        help='The password of the MQTT broker.')
    args = parser.parse_args()

    return args


def main(stdscr):
    stdscr.clear()
    args = parse_args()
    log_manager = LogManager(
        findmy_files=[os.path.expanduser(f) for f in FINDMY_FILES],
        store_keys=args.store_keys,
        timestamp_key=args.timestamp_key,
        log_folder=args.log_folder,
        name_keys=args.name_keys,
        name_separator=NAME_SEPARATOR,
        json_layer_separator=JSON_LAYER_SEPARATOR,
        null_str=NULL_STR,
        date_format=DATE_FORMAT,
        no_date_folder=args.no_date_folder,
        mqtt_broker_ip=args.mqtt_broker_ip,
        mqtt_broker_port=args.mqtt_broker_port,
        mqtt_broker_username=args.mqtt_broker_username,
        mqtt_broker_password=args.mqtt_broker_password)

    while True:
        log_manager.refresh_log()
        latest_log, log_cnt = log_manager.get_latest_log()
        table = []
        for name, log in latest_log.items():
            latest_time = log[args.timestamp_key]
            if isinstance(latest_time, int) or isinstance(latest_time, float):
                latest_time = datetime.fromtimestamp(
                    float(latest_time) / 1000.)
                latest_time = latest_time.strftime(TIME_FORMAT)
            table.append([name, latest_time, log_cnt[name]])
        table = tabulate(
            table,
            headers=['Name', 'Last update', 'Log count'],
            tablefmt="github")

        stdscr.erase()
        try:
            stdscr.addstr(
                0, 0, f'Current time: {datetime.now().strftime(TIME_FORMAT)}')
            stdscr.addstr(1, 0, table)
        except:
            pass
        stdscr.refresh()

        time.sleep(float(args.refresh) / 1000)


if __name__ == "__main__":
    curses.wrapper(main)
