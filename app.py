from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import subprocess

app = Flask(__name__)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'wp_config.json')
SUBMISSIONS_PATH = os.path.join(os.path.dirname(__file__), 'submissions')

USERNAME = 'pi'
PASSWORD = 'raspberry'


def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"teams": {"blue": [], "red": []}}


def list_zip_files():
    try:
        # print("ZipFiles: ", SUBMISSIONS_PATH)
        return sorted([f for f in os.listdir(SUBMISSIONS_PATH) if f.endswith('.zip')])
    except Exception as e:
        print(f"Error listing submissions: {e}")
        return []


@app.route('/', methods=['GET'])
def index():
    config = load_config()
    zip_files = list_zip_files()
    return render_template('index.html', teams=config['teams'], zip_files=zip_files)


@app.route('/submit', methods=['POST'])
def submit():
    team = request.form.get('team')
    zip_file = request.form.get('zip_file')
    if team and zip_file:
        handle_submission(team, zip_file)
    return redirect(url_for('index'))


@app.route('/agent_action', methods=['POST'])
def agent_action():
    config = load_config()
    team = request.form.get('team')
    boat_id = request.form.get('boat_id')
    boat_name = request.form.get('boat_name')
    boat_ip = request.form.get('boat_ip')
    boat_port = request.form.get('boat_port')
    action = request.form.get('action')
    print(f"Team: {team}, Boat ID: {boat_id}, Boat Name: {boat_name}, Boat IP: {boat_ip}, Boat Port: {boat_port}, Action: {action}")
    command = ''

    if config['shore_ip'] == 'localhost':    
        command = f"python submission_runner.py --entry_name=test.zip --sim --color={team} --boat_id={boat_id} --boat_name={boat_name} --timewarp=4 --shore_ip={config['shore_ip']} --boat_ip={boat_ip} --boat_port={boat_port}"#f"sshpass -p '{PASSWORD}' rsync -av --progress ./submissions/{filename} {USERNAME}@{ip}:{dest_path}"
    else:
        command = f"python submission_runner.py --entry_name=test.zip --color={team} --boat_id={boat_id} --boat_name={boat_name} --timewarp=1 --shore_ip={config['shore_ip']} --boat_ip={boat_ip} --boat_port={boat_port}"
        command = f"sshpass -p {PASSWORD} ssh {USERNAME}@{boat_ip} " + command
    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f"{command}; exec bash"])
    return redirect(url_for('index'))


def handle_submission(team, zip_file):
    print(f"Received submission for {team} team: {zip_file}")
    config = load_config()
    file_path = ""
    if config['shore_ip'] == 'localhost': #We are running in sim copy team files to local dirs
        #Ensure the folder can only ever have one entry 
        subprocess.run(["rm", "-rf", f"~/USV_Deploy_UI/{team}_entry"])
        subprocess.run(["mkdir", "-p", f"~/USV_Deploy_UI/{team}_entry"])


        if 'red' == team:
            file_path = '~/USV_Deploy_UI/red_entry/test.zip'
        else:
            file_path = '~/USV_Deploy_UI/blue_entry/test.zip'
    if config['shore_ip'] == 'localhost':
        command = "cp ~/USV_Deploy_UI/submissions/"+zip_file+" "+file_path+" ; exec bash"
        subprocess.Popen(['gnome-terminal','--', 'bash', '-c', command]) #Launch MacOS/Linux machines 
    else:
        for bot in config['teams'][team]:
            command = "sshpass -p "+PASSWORD+" rsync -av --progress ./submissions/{zip_file} {USERNAME}@{bot['ip']}:~/entries/ ; exec bash"
            subprocess.Popen(['gnome-terminal','--', 'bash', '-c', command]) #Launch MacOS/Linux machines 


@app.route('/get_rsync_command', methods=['POST'])
def get_rsync_command():
    config = load_config()
    data = request.json
    team = data['team']
    boat_id = data['boat_id']
    boat_name = data['boat_name']
    boat_ip = data['boat_ip']
    boat_port = data['boat_port']
    action = data['target']
    path = "~/USV_Deploy_UI/"
    path += "blue_entry/" if team == 'blue' else "red_entry/"
    
    if config['shore_ip'] == 'localhost':    
        command = f"python submission_runner.py --sim --boat_id={boat_id} --boat_name={boat_name} --timewarp=4 --shore_ip={config['shore_ip']} --boat_ip={boat_ip} --boat_port={boat_port}"#f"sshpass -p '{PASSWORD}' rsync -av --progress ./submissions/{filename} {USERNAME}@{ip}:{dest_path}"
    else:
        command = f"python submission_runner.py --boat_id={boat_id} --boat_name={boat_name} --timewarp=1 --shore_ip={config['shore_ip']} --boat_ip={boat_ip} --boat_port={boat_port}"
        #command = f"sshpass -p '{PASSWORD}' "
    return jsonify({'command': command})


if __name__ == '__main__':
    app.run(debug=True)
