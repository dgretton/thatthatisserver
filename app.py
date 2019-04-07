import os
import sys
import json

#derp_module_path = os.path.abspath('..')
#if derp_module_path not in sys.path:
#    sys.path.append(derp_module_path)

from flask import Flask, render_template, request, jsonify

from that_is_not_calculus import gen_thatthatis
app = Flask(__name__)

@app.route("/thatthatis/")
def that_is_svc():
    response = jsonify([gen_thatthatis() for i in range(3)])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(debug=True)
