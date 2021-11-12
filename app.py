from flask import Flask, request, render_template
import json
import os
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdefg'


@app.route("/")
def root():
	return render_template('Index.html')


@app.route("/upload_to_swarm", methods=['POST'])
def upload_to_swarm():
	header = {'Content-Type': 'application/octet-stream'}
	data = {'file': request.files['file']}
	response = requests.post('http://localhost:8500/bzz:/', files=data, headers=header)
	return json.dumps({'swarm_id': response.text, 'status': 'success'})


@app.route("/download_from_swarm", methods=['POST'])
def download_from_swarm():
	swarm_id = request.json["swarm_id"]
	client_id = request.json["client_id"]
	is_global = request.json["is_global"]
	client_address = request.json["client_address"]
	swarm_url = f'http://localhost:8500/bzz:/{swarm_id}/'
	swarm_return = requests.get(swarm_url)

	strs = swarm_return.text.splitlines()
	filename = strs[1][strs[1].rindex('"', 0, -1) + 1:-1]
	with open(f'./models/{filename}', 'wb') as f:
		# [3, nLines-1)
		l_idx = swarm_return.content.find(b'\x93')
		r_idx = swarm_return.content.rfind(b'AtqBbetqCb.')
		f.write(swarm_return.content[l_idx: r_idx+11])
	
	file = {'file': open(f'models/{filename}', 'rb')}
	data = {'client_id': client_id, 'is_global': is_global}
	print(f"start sending model.")
	response = requests.post(f'http://{client_address}/receive', files=file, data=data)
	return json.dumps({'status': 'success'})


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port='40000')

