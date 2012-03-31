from user import *
import json
from twilio.rest import TwilioRestClient    # TODO: Move this into an SMS nofitication handler


twilio_settings = {}


def notify_user(user_name, message):
    global twilio_settings
    print 'Looking for user %s' % user_name
    user = User.get_by_user_name(user_name)
    if not user:
        print 'Error: Unknown user_name "%s"' % user_name
        return False
    print 'Found user "%s"' % user_name

    client = TwilioRestClient(twilio_settings['account_sid'], twilio_settings['auth_token'])
    sms_message_response = client.sms.messages.create(from_=twilio_settings['from_number'], to=user.phone_number(), body=message)

    return True

print "Loading Twilio Secrets"

secrets_file = open('twilio_secrets.cfg')
twilio_settings = json.load(secrets_file)
secrets_file.close()

print 'Twilio Account SID: %s' % twilio_settings['account_sid']
print 'Twilio From Number: %s' % twilio_settings['from_number']

