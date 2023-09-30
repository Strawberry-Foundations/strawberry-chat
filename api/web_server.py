from flask import *
import os 

server_dir      = os.path.dirname(os.path.realpath(__file__))
json_file       = server_dir + "/config.json"
json_api_dir    = server_dir + "/json/"

address         = json.load(open(json_file))["address"]
port            = json.load(open(json_file))["port"]
debug_mode      = json.load(open(json_file))["debug_mode"]

app             = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="pages")

def ajson(json_file):
    return json.load(open(json_api_dir + json_file + ".json"))

@app.route('/', methods=['GET', 'POST'])
def index():
    return "Strawberry API Servers"

@app.route('/v1/', methods=['GET', 'POST'])
def v1_index():
    return ajson("api_index")

@app.route('/v1/server/verified', methods=['GET', 'POST'])
def server_verified():
    server = request.args.get('addr')
    
    if server in json.load(open(json_api_dir + "verified_server.json"))["servers"]:
        return "True"
    else:
        return "False"

@app.route('/v1/utils/user/ip', methods=['GET'])
def user():
    return jsonify({'ip': request.remote_addr}), 200 

@app.route('/v1/versions', methods=['GET', 'POST'])
def versions():
    return ajson("versions")

if __name__ == "__main__":
    app.run(host=address, port=port, debug=debug_mode)