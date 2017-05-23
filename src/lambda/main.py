#!/usr/bin/env python2.7

#from urllib import quote
import json
#from requests import get
import pprint
#import re
import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr
import decimal

pp = pprint.PrettyPrinter(indent=4)

dynamodb = None
table = None



# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Get's the help section

    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Sends the request to one of our intents
    if intent_name == "FindDevice":
        return get_find_device_response(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        print(intent_name)
        return build_response({},  build_speechlet_response(None, 'not ok'))

def on_session_ended(session_ended_request, session):
    # When the User decides to end the session, this is the function that is
    # called.
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------


def get_welcome_response():
    """ Helps the User Find out what they can say, and how to use
            the program, Sends a Card with that data as well"""
    session_attributes = {}
    card_title = "Andy"
    speech_output = "Ask Dude where's your device, such as your car."
    reprompt_text = "Dude, where's your car?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    print('handle_session_end_request')
    should_end_session = True
    return build_response({}, build_speechlet_response(
        None, None, None, should_end_session))


def get_find_device_response(intent):

    # response = get('https://pun.andrewmacheret.com')
    # data = response.json()
    # pp.pprint(data)

    # pun = data['pun']

    # speech = build_speechlet_response("Dude, Where's My Car?", pun)
    # return build_response({}, speech)

    device = None
    other_device = None

    device = intent['slots']['DEVICE'].get('value')
    if device is None or not (device == 'car' or device == 'phone'):
        return build_response({},  build_speechlet_response(None, "I can only find your car or your phone, dude"))
    if device == 'car':
        other_device = 'phone'
    else:
        other_device = 'car'

    device_response = query_for_device_location(device)
    if device_response.get('error') != None:
        return build_response({},  build_speechlet_response(None, "Where's you're %s, dude?" % device))

    other_device_response = query_for_device_location(other_device)
    if other_device_response.get('error') != None:
        return build_response({},  build_speechlet_response(None, "Where's you're %s, dude?" % device))

    location_dy = device_response['location'][0] - other_device_response['location'][0]
    location_dy_dir_name = 'North' if location_dy > 0 else 'South'
    location_dx = device_response['location'][1] - other_device_response['location'][1]
    location_dx_dir_name = 'East' if location_dy > 0 else 'West'

    text = "Your %s is located at %.3g degrees %s and %.3g degrees %s from your %s" % (device, location_dx, location_dy_dir_name, location_dy, location_dx_dir_name, other_device)
    return build_response({}, build_speechlet_response("Dude, where's my %s" % (device), text))


def query_for_device_location(device):
    global dynamodb
    global table

    if dynamodb == None:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    if table == None:
        table = dynamodb.Table('dude_device')

    try:
        response = table.query(
            KeyConditionExpression=Key('device_name').eq(device),
            Limit=1
        )
        pp.pprint(response)
        if len(response['Items']) == 0:
            return {
                "error": "No records found for device_name %s" % device
            }
        return {
            "location": response['Items'][0]['location']
        }
    except botocore.exceptions.ClientError as e:
        error = e.response['Error']['Message']
        pp.pprint(e)
        return {
            "error": error
        }





# --------------- Helpers that build all of the responses ----------------


def build_speechlet_response(title, output, reprompt_text="", should_end_session=True):
    if output == None:
        return {
            'shouldEndSession': should_end_session
        }
    elif title == None:
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }
    else:
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'card': {
                'type': 'Simple',
                'title':  title,
                        'content': output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


