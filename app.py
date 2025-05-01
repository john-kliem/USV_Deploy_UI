from flask import Flask, render_template, request, redirect, url_for
import json
import os
import subprocess

app = Flask(__name__)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'wp_config.json')
SUBMISSIONS_PATH = os.path.join(os.path.dirname(__file__), 'submissions')

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

def handle_submission(team, zip_file):
    print(f"Received submission for {team} team: {zip_file}")
    config = load_config()
    config['team']
    for bot in config['teams']:
        command = "sshpass -p 'raspberry' rsync -av --progress ./submissions/{zip_file} {username}@{config['teams']['ip']}:/entries/"
        subprocess.Popen(['gnome-terminal','--', 'bash', '-c', command]) #Launch MacOS/Linux machines 
    # Do something with the file here: unzip, copy, run, etc.


if __name__ == '__main__':
    app.run(debug=True)
