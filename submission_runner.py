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
        #TODO Find command to locate logs and copy all log files
        entry_docker.kill()
    sys.exit(0)


def run_game(entry_path, sim, color, boat_id, boat_name, timewarp, shore_ip, boat_ip, boat_port):
    global entry_docker
    client = docker.from_env()
    entry_docker = client.containers.run('jkliem/wp25:v2',command='sleep infinity', detach=True, network_mode='host')
    #entry_docker.start()
    subprocess.run(['docker','cp', entry_path, str(entry_docker.short_id)+':/home/moos/working_dir/test.zip']) #Copy file into new docker
    #Unzip copied entry
    print(entry_docker.exec_run('unzip /home/moos/working_dir/test.zip -d /home/moos/working_dir/'))
    if sim:
        arguments = '--sim'
    else:
        arguments = ' '
    arguments += ' --color=' + color
    arguments += ' --boat_id=' + boat_id
    arguments += ' --boat_name=' + boat_name
    arguments += ' --timewarp=' + str(timewarp)
    arguments += ' --shore_ip ' + shore_ip 
    arguments += ' --boat_ip='+ boat_ip 
    arguments += ' --boat_port=' + str(boat_port)
    print("Launching with Arguments: ", arguments)
    print("Entry Docker: ", entry_docker.short_id)
    entry_docker.exec_run('sh -c "python3 -u pyquaticus_moos_launcher.py '+arguments+' > out.txt 2>&1"', detach=True)# Run Entry
    return 


if __name__ == "__main__":
    entry_folder = './entries/'
    parser = argparse.ArgumentParser(description='Deploy the MCTF2025 Policies on USV\'s via MOOS-IvP')
    parser.add_argument('--entry_name', required=True, type=str, help='Name of zip to be loaded in (do not add leading /)')
    parser.add_argument('--sim', action='store_true', help="Specify if simulation or not.")
    parser.add_argument('--color', required=True, choices=['red', 'blue'], help="Specify if red or blue team is the trained agent.")
    parser.add_argument('--boat_id', required=True, choices=["blue_one", "blue_two", "blue_three", "red_one", "red_two", "red_three"], help="Specify the boat id.")
    parser.add_argument('--boat_name', required=False, choices=['s', 't', 'u', 'v', 'w', 'x', 'y', 'z'], help="Specify the boat name.")
    parser.add_argument('--timewarp', required=True, type=int, default=4, help='Specify the timewarp.')
    parser.add_argument('--shore_ip', required=True, type=str, default='localhost', help='Specify the shoreside IP.')
    parser.add_argument('--boat_ip', required=True, type=str, default='localhost', help='Specify the USV IP.')
    parser.add_argument('--boat_port', required=True, type=int, default=9012, help='Specify the USV Port to Use.')
    args = parser.parse_args()
    entry_path = args.entry_name
    signal.signal(signal.SIGINT, signal_handler)
    run_game(entry_path, args.sim, args.color, args.boat_id, args.boat_name, args.timewarp, args.shore_ip, args.boat_ip, args.boat_port)
    signal.pause()