import os
import sys
import json

das_module_path = os.path.abspath('./stardas_v0')
if das_module_path not in sys.path:
    sys.path.append(das_module_path)

#from stardas import dastag
from flask import Flask, render_template, request, jsonify

from that_is_not_calculus import gen_thatthatis
app = Flask(__name__)

@app.route("/thatthatis/")
def that_is_svc():
    response = jsonify([gen_thatthatis() for i in range(3)])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/genmeadastag/")
def host_dastag():
    return str((os.path.abspath('./stardas_v0'), sys.path))
    return dastag()

if __name__ == '__main__':
    app.run(debug=True)
