import os
from flask import Flask, jsonify, request
import json
import requests

#export NUMBERS='["+351xxxxx", "+351yyyyyy"]'
#export URLSMSGATEWAY=<url>
#export TEAMSWEBHOOK=<url>
#export ENVIRONMENTNAME=<environment name>

app = Flask(__name__)

@app.route('/gateway', methods=['POST'])
def save_dev():
    ENVIRONMENTNAME=str(os.environ['ENVIRONMENTNAME'])
    data = request.get_json()
    print("Body Request: "+str(data))
    info = {}

    # Filter information
    info['Receiver'] = data['receiver']
    if 'commonAnnotations' in data and 'message' in data['commonAnnotations']:
        info['commonAnnotations']=data['commonAnnotations']['message']
    else:
        info['commonAnnotations'] =None

    info['alerts'] = []
   # info['alerts'].append(data['status'])
    for alerts in data['alerts']:
        labels=alerts['labels']
        labels['status']=alerts['status']

        if 'annotations' in alerts and 'message' in alerts['annotations']:
            labels['annotations'] = alerts['annotations']['message']
        if 'annotations' in alerts and 'description' in alerts['annotations']:
            labels['annotations-description'] = alerts['annotations']['description']
        if 'annotations' in alerts and 'summary' in alerts['annotations']:
            labels['annotations-summary'] = alerts['annotations']['summary']
        info['alerts'].append(labels)



    teamsMessage=createMessageToTeams(info,ENVIRONMENTNAME)
    teamsStatus=sendNotificationToTeams(teamsMessage)
    info['TeamsStatus'] = []
    info['TeamsStatus'].append(str(teamsStatus.text))
    info['TeamsStatus'].append(str(teamsStatus))

    smsMessage=createNotificationViaSMS(info)
    smsStatus=sendSMSMessage(smsMessage,ENVIRONMENTNAME)
    info['smsStatus'] = []
    info['smsStatus'].append(str(smsStatus.text))
    info['smsStatus'].append(str(smsStatus))
    print(info)



    return jsonify(info), 201

def sendSMSMessage(smsMessage,sender_id):
    print("\nsendSMSMessage:\n")
    print("<smsMessage>: "+smsMessage)
    numbers = (os.environ['NUMBERS'])

    print("<numbers>:"+str(numbers))
    URLSMSGateway = str(os.environ['URLSMSGATEWAY'])

    payload = "{\n\"receivers\":"+numbers+",\n\"message\": \""+str(smsMessage)+"\",\n\"sender_id\":\""+sender_id+" Environment\"\n}"

    print("payload " +payload)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", URLSMSGateway, headers=headers, data=payload)

    print("Sending sms response: "+str(response.text))
    return response


def createNotificationViaSMS(message):

    sms = 'Sent by: ' + str(message['Receiver']) + '\n'
    sms = sms + 'Message: ' + str(message['commonAnnotations']) + '\n'
    sms = str(sms) + 'Total of alerts: ' + str(len(message['alerts'])) + '\n\n'

    for i, alert in enumerate(message['alerts'], start=1):
        sms = sms + '\tAlert ' + str(i) + '\n'
        sms= str(sms) + 'Alertname: ' + str(alert['alertname'])+ '\n'
        sms = str(sms) + 'Severity: ' + str(alert['severity']) + '\n'
    print("SMS Message to send: "+str(sms)+"\n\n")
    return sms

def sendNotificationToTeams(message):
    teamsWebhook=str(os.environ['TEAMSWEBHOOK'])
    data=json.dumps(message)
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", teamsWebhook, headers=headers, data=data)
    print("Status Response: "+str(response))
    print("Content: "+str(response.text))
    return response

def createMessageToTeams(message,ENVIRONMENTNAME):
    list = []
    #create list alerts
    for i,fullAlert in enumerate(message['alerts'],start=1):
        if i >1:
            elements = {'name': "________________________", 'value': '\n'}
            list.append(elements)
            elements = {'name': "________________________", 'value': '\n'}
            list.append(elements)
        elements = {'name': "ALERT", 'value': i}
        list.append(elements)
        for key, value in fullAlert.items():
            elements = {'name': key, 'value': value}
            list.append(elements)

    data = {}
    data['text'] = " "

    data.update({"themeColor": "c9d700"}) #yellow alert c9d700
    data.update({"themeColor": "d70000"}) # red alert

    data["sections"] = []
    data["sections"].append(({"activityTitle": "Team Stratus "}))
    data["sections"].append(({"activitySubtitle": "Environment: "+str(ENVIRONMENTNAME)}))
    data["sections"].append(({"activityImage": "https://pngriver.com/wp-content/uploads/2018/04/Download-Alert-PNG.png"}))
    data["sections"].append(({"activitySubtitle": message['commonAnnotations']}))
    data["sections"].append(({"facts": list}))

    return data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
