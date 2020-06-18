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
    info = {}

    # Filter information
    info['Receiver'] = data['receiver']
    info['commonAnnotations']=data['commonAnnotations']['message']
    info['alerts'] = []
    for alerts in data['alerts']:
        info['alerts'].append(alerts['labels'])

    teamsMessage=createMessageToTeams(info,ENVIRONMENTNAME)
    sendNotificationToTeams(teamsMessage)

    smsMessage=createNotificationViaSMS(info)
    print("\nSMS message: \n"+str(smsMessage)+"\nEnd SMS\n")
    sendSMSMessage(smsMessage,ENVIRONMENTNAME)


    return jsonify(info), 201

def sendSMSMessage(smsMessage,sender_id):
    print("\nsendSMSMessage:\n")
    print("<smsMessage>: "+smsMessage)
    numbers = (os.environ['NUMBERS'])

    print("<numbers>:"+str(numbers))
    URLSMSGateway = str(os.environ['URLSMSGATEWAY'])

    payload = "{\n\"receivers\":"+numbers+",\n\"message\": \""+str(smsMessage)+"\",\n\"sender_id\":\""+sender_id+"\"\n}"

    print("payload " +payload)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", URLSMSGateway, headers=headers, data=payload)

    print(response.text.encode('utf8'))


def createNotificationViaSMS(message):

    sms = 'Sent by: ' + str(message['Receiver']) + '\n'
    sms = sms + 'Message: ' + str(message['commonAnnotations']) + '\n'
    sms = str(sms) + 'Total of alerts: ' + str(len(message['alerts'])) + '\n\n'

    for i, alert in enumerate(message['alerts'], start=1):
        sms = sms + '\tAlert ' + str(i) + '\n'
        sms= str(sms) + 'Alertname: ' + str(alert['alertname'])+ '\n'
        sms = str(sms) + 'Severity: ' + str(alert['severity']) + '\n'

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
    data["sections"].append(({"activityTitle": "Stratus Team "}))
    data["sections"].append(({"activitySubtitle": "Environment: "+str(ENVIRONMENTNAME)}))
    data["sections"].append(({"activityImage": "https://pngriver.com/wp-content/uploads/2018/04/Download-Alert-PNG.png"}))
    data["sections"].append(({"activitySubtitle": message['commonAnnotations']}))
    data["sections"].append(({"facts": list}))

    return data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
