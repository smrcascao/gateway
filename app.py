import flask
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/gateway', methods=['POST'])
def save_dev():
    data = request.get_json()
    headers= flask.request.headers
    print("\n############\nBody: "+str(data)+"\n")
    print("\n############\nHeaders: " + str(headers)+"\n############\n")

    return jsonify(data), 201



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8000)
