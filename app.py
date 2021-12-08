from flask import Flask, request, render_template
import json
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdefg'


@app.route("/")
def root():
    return render_template('Index.html')


def upload_to_swarm():
    header = {'Content-Type': 'application/octet-stream'}
    for elem in request.files:
        file_name = elem
    data = {'file': request.files[file_name]}
    print(data)
    response = requests.post('http://localhost:8500/bzz:/', files=data, headers=header)
    return json.dumps({'swarm_id': response.text, 'status': 'success'})


@app.route("/download_from_swarm", methods=['POST'])
def download_from_swarm():
    swarm_id = request.json["swarm_id"]
    is_global = request.json["is_global"]
    client_address = request.json["client_address"]
    print(client_address)
    swarm_url = f'http://localhost:8500/bzz:/{swarm_id}/'
    swarm_return = requests.get(swarm_url)

    strs = swarm_return.text.splitlines()
    filename = strs[1][strs[1].rindex('"', 0, -1) + 1:-1]
    print(f"filename: {filename}")
    # idx range is [l_idx, r_idx]
    l_idx = swarm_return.content.find(b'start_of_file') + 13
    r_idx = swarm_return.content.find(b'end_of_file')
    model_data = swarm_return.content[l_idx: r_idx]
    file = {filename: model_data}
    client_id = -1
    if is_global is False:
        client_id_ridx = filename.find('.pkl')
        client_id_str = filename[:client_id_ridx]
        client_id = (int)(client_id_str)
    print(f'client_id: {client_id}')
    data = {'client_id': client_id, 'is_global': is_global}
    print(f"start sending model.")
    response = requests.post(f'http://{client_address}/receive', files=file, data=data)
    return json.dumps({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='40000')
