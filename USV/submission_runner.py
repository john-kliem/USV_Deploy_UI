import docker
import subprocess
import time
import sys
import socket
import random
import argparse
import signal
import sys

entry_docker = None
def signal_handler(sig, frame):
    if entry_docker:
        print('Closing Docker')
        entry_docker.kill()
    sys.exit(0)


def run_game(entry_path, shore_ip, boat_ip, boat_port):
    global entry_docker
    print("Team 1 Path: ", team_one['path'],  " Team 2 Path: ", team_two['path'])
    client = docker.from_env()
    entry_docker = client.containers.run('jkliem/wp25:latest', command="sleep infinity", detach=True, network_mode='host')
    subprocess.run(['docker','cp', entry_path, str(entry_docker.short_id)+':/home/moos/workingdir/test.zip']) #Copy file into new docker
    entry_docker.exec_run('sh -c "python3.10 -u d.py '+str(port2)+' > out.txt 2>&1"', detach=True)# Run Entry
    return 


if __name__ == "__main__":
    entry_folder = './entries/'
    parser = argparse.ArgumentParser(description='Deploy the MCTF2025 Policies on USV\'s via MOOS-IvP')
    parser.add_argument('entry_name', help='Name of zip to be loaded in (do not add leading /)', action='store_true')
    parser.add_argument('shore_ip', help='Shoreside IP Address')
    parser.add_argument('boat_ip', help='USV\'s IP Address')
    parser.add_argument('boat_port', help='USV\'s Port')
    args = parser.parse_args()
    entry_path = entry_folder += args.entry_name
    signal.signal(signal.SIGINT, signal_handler)
    run_game(entry_path, shore_ip, boat_ip, boat_port)
    signal.pause()
    
    


