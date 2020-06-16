import os
import flask
from flask import Flask, jsonify, request
import json
import requests

app = Flask(__name__)

@app.route('/gateway', methods=['POST'])
def save_dev():
    data = request.get_json()
    headers= flask.request.headers
    print("\n##### Body: #######\n "+str(data)+"\n")
    print("\n##### Headers: #######\n " + str(headers)+"\n############\n")
    sendNotificationToTeams(data)

    return jsonify(data), 201


def sendNotificationToTeams(message):
    teamsWebhook=str(os.environ['TEAMSWEBHOOK'])
    print(teamsWebhook)

    data = {}
    data['text'] = str(message)
    data.update({"themeColor": "c9d700"}) #yellow alert c9d700
    data.update({"themeColor": "d70000"}) # red alert

    data["sections"] = []
    data["sections"].append(({"activityTitle": "![TestImage](https://pngriver.com/wp-content/uploads/2018/04/Download-Alert-PNG.png)ALERT cluster Stoped"}))
    data["sections"].append(({"activityImage": "https://pngriver.com/wp-content/uploads/2018/04/Download-Alert-PNG.png"}))
    data["sections"].append(({"activitySubtitle": "Stratus Team"}))

    print(data)
    data=json.dumps(data)
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", teamsWebhook, headers=headers, data=data)
    print("Status Response: "+str(response))
    print("Content: "+str(response.text))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
