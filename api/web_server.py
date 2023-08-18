from flask import *
import os 

server_dir      = os.path.dirname(os.path.realpath(__file__))
json_file       = server_dir + "/config.json"

address         = json.load(open(json_file))["address"]
port            = json.load(open(json_file))["port"]
debug_mode      = json.load(open(json_file))["debug_mode"]

app             = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="pages")


@app.route('/', methods=['GET', 'POST'])
def index():
    return "index"

@app.route('/v1/test', methods=['GET', 'POST'])
def test():
    return "stbchat"

if __name__ == "__main__":
    app.run(host=address, port=port, debug=debug_mode)