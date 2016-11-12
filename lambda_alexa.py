"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import urllib2
import json

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    response = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
    print(response)
    return response


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Skills Kit sample. " \
                    "Please tell me your favorite color by saying, " \
                    "my favorite color is red"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your favorite color by saying, " \
                    "my favorite color is red."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_txns():
    content = urllib2.urlopen("http://intuit-mint.herokuapp.com/api/v1/user/transactions").read()
    return json.loads(content)

def get_net_income(intent, session):
    txns = get_txns()
    income = sum([txn['amount'] for txn in txns if txn['amount'] > 0])

    session_attributes = {}
    card_title = "Net Income"
    speech_output = "Your net income is ${}".format(income)

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask me by saying whats my net income"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_net_expenditure(intent, session):
    txns = get_txns()
    expenditure = -sum([txn['amount'] for txn in txns if txn['amount'] < 0])

    session_attributes = {}
    card_title = "Net Expense"

    speech_output = "Your net expenditure is ${}".format(expenditure)
    reprompt_text = "Please ask me by saying whats my net income"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_type(flag):
    if flag == 1:
        return "You top sources of incomes are..."
    else:
        return "You spent the most on..."

def get_stats_helper(mask):
    cat = dict()
    txns = get_txns()

    for txn in txns:
        if mask * txn['amount'] > 0:
            txn_cat = txn['category']
            cat[txn_cat] = cat.get(txn_cat, 0) + txn['amount']

    stat = sorted(cat.items(), key=lambda x:x[1], reverse=(mask==1))[:3]
    stat = [(s[0],int(mask*s[1])) for s in stat]
    items = ''
    for s in stat:
        items += s[0]+' $'+str(s[1])+","

    resp = '{} {}.'.format(get_type(mask), items[:len(items)-1])
    print(resp)
    return resp

def get_stats(intent, session):
    intent = intent['intent']
    type_dict = dict(income=1, expenditure=-1, expense=-1, default=0)

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    flag = type_dict['default']
    print(intent)
    if 'Type' in intent['slots'] and 'value' in intent['slots']['Type']:
        flag = type_dict.get(intent['slots']['Type']['value'].lower(), 0)

    if flag == 0:
        speech_output = get_stats_helper(type_dict['income'])
        speech_output += get_stats_helper(type_dict['expenditure'])
    else:
        speech_output = get_stats_helper(flag)

    reprompt_text = "You can ask me statistics of your spending by saying, " \
                    "my stats, get stats, get stats for income, get stats " \
                    "for expenditure."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_expense_for(intent, session):

    intent = intent['intent']
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    txns = get_txns()
    if 'Category' in intent['slots']:
        query = intent['slots']['Category']['value'].lower()
        interested_txns = [txn['amount'] for txn in txns
                                    if query in txn['category'].lower() or
                                       query in txn['name'].lower()]
        if len(interested_txns):
            expenditure = -sum(interested_txns)
            speech_output = "Your net expenditure for {} is ${}. " \
                            "You can ask me expense of individual categories" \
                            " by saying, what's the expense for Uber or Lyft " \
                            "etc.".format(query.lower(), expenditure)
        else:
            speech_output = "I'm not sure if you have an expense with "\
                            "category: {0}. Please try again.".format(query)

    else:
        speech_output = "I'm not sure if you have asked me expense for a " \
                        "category. Please try again."

    reprompt_text = "You can ask me expense of a particular category by saying, " \
                    "what's the expense for Uber or Lyft,"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

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
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    intent_fn_map_dict = dict()
    intent_fn_map_dict['IncomeIntent'] = get_net_income
    intent_fn_map_dict['ExpenseIntent'] = get_net_expenditure
    intent_fn_map_dict['CategoryExpenseIntent'] = get_expense_for
    intent_fn_map_dict['StatsIntent'] = get_stats
    intent_fn_map_dict['AMAZON.HelpIntent'] = get_welcome_response
    intent_fn_map_dict['AMAZON.CancelIntent'] = handle_session_end_request
    intent_fn_map_dict['AMAZON.StopIntent'] = handle_session_end_request

    print(intent_name)
    if intent_name in intent_fn_map_dict:
        return intent_fn_map_dict[intent_name](intent_request, session)
    else:
        raise ValueError("Invalid intent")
    # Dispatch to your skill's intent handlers
    # if intent_name == "MyColorIsIntent":
    #     return set_color_in_session(intent, session)
    # elif intent_name == "WhatsMyColorIntent":
    #     return get_color_from_session(intent, session)
    # elif intent_name == "AMAZON.HelpIntent":
    #     return get_welcome_response()
    # elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
    #     return handle_session_end_request()
    # else:



def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


get_stats_helper(1)