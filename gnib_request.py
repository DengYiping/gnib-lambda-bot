import requests as rq
import time
import urllib3
import boto3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GNIB_APPOINTMENT_URL = 'https://burghquayregistrationoffice.inis.gov.ie/Website/AMSREG/AMSRegWeb.nsf/(getAppsNear)?readform&cat=All&sbcat=All&typ=New&k=AE1BC886D4C558A0F9C13DBE8F5B1230&p=227D175CE082121CEA4982CDC75EF75A&_=1569063836652'

GNIB_EMPTY_RESPONSE = {'empty': 'TRUE'}
TOPIC_ARN = 'arn:aws:sns:eu-west-1:381487325561:Gnib'

def request_gnib():
    url = os.getenv('GNIB_URL', GNIB_APPOINTMENT_URL)
    rq_result = rq.get(url, verify = False)
    if rq_result.ok:
        return rq_result.json()
    else:
        return None

def main():
    print('Checking gnib appointments')
    result = request_gnib()
    while result == GNIB_EMPTY_RESPONSE:
        print('Checking gnib appointments')
        result = request_gnib()
        time.sleep(5)
    print('Found differences, maybe there is a appointment:\n{}'.format(result))

def publish_message(message):
    sns = boto3.client('sns')
    sns.publish(
        TopicArn = TOPIC_ARN,
        Message = message)

def handler(event, context):
    if 'testing' in event:
        result = request_gnib()
        msg = 'Testing result: {}'.format(str(result))
        publish_message(msg)
    else:
        result = request_gnib()
        if result != GNIB_EMPTY_RESPONSE:
            publish_message('find appointment: {}'.format(str(result)))
            print('Find appointment: {}'.format(str(result)))
        else:
            print('Nothing fancy is happening now.')

if __name__ == '__main__':
    main()
