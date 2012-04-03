import tornado.web
import requests
from conf import settings
import json
import logging

class ExternalEventHandler(tornado.web.RequestHandler):
    # implement common functionality here: a generic getuser method, perhaps?
    def getuser(self, **kwargs):
        url = "http://" + settings.users['host'] + ":" + str(settings.users['port']) + "/"
        users_json = requests.get(url, params=kwargs)
        users = json.loads(users_json.text)
        if len(users) > 0:
            return users[0]
        else:
            return None

    def send_event(self, **event):
        url = "http://" + settings.eventnetwork['host'] + ":" + str(settings.eventnetwork['port']) + "/event/"
        url += event['domain'] + '/'
        url += event['name']
        del event['domain'], event['name']
        return requests.post(url, data=event)


""" TwilioHandler: processes SMS messages sent from users

Data sent from Twilio looks like this:

    AccountSid = ACb45422a1828b4fa49fb12f7adb0c05ed
    Body = this+is+a+test
    ToZip = 84003
    FromState = WA
    ToCity = PLEASANT+GROVE
    SmsSid = SMa8a06fd8d6bf468a2a0a73fe95d66b28
    ToState = UT
    To = +18017011383
    ToCountry = US
    FromCountry = US
    SmsMessageSid = SMa8a06fd8d6bf468a2a0a73fe95d66b28
    ApiVersion = 2010-04-01
    FromCity = KENT
    SmsStatus = received
    From = +12532345072
    FromZip = 98042

"""
class TwilioHandler(ExternalEventHandler):
    def post(self):
        logging.info('TwilioHandler.post: Post arguments = "%s"' % self.request.arguments)
        # TODO: package data into an internal event and forward it
        # print self.request.body
        print "Getting user: " + self.get_argument("From")
        user = self.getuser(phone=self.get_argument("From"))
        if user is None:
            print "No user found"
        else:
            self.send_event(domain="user", name="new_reminder",
                    user_name=user['username'], reminder_text=self.get_argument("Body"))
            


"""
Foursquare handler: receives location updates via Foursquare's realtime API

Data sent by Foursquare looks like this:

{
  "venue": {
    "verified": true, 
    "name": "foursquare HQ", 
    "url": "https://foursquare.com", 
    "contact": {
      "twitter": "foursquare"
    }, 
    "location": {
      "city": "New York", 
      "country": "United States", 
      "postalCode": "10012", 
      "state": "NY", 
      "crossStreet": "at Prince St.", 
      "address": "568 Broadway", 
      "lat": 40.724380483567131, 
      "lng": -73.9974045753479
    }, 
    "stats": {
      "tipCount": 54, 
      "checkinsCount": 5200, 
      "usersCount": 1274
    }, 
    "id": "4ef0e7cf7beb5932d5bdeb4e", 
    "categories": [
      {
        "pluralName": "Tech Startups", 
        "primary": true, 
        "name": "Tech Startup", 
        "parents": [
          "Professional & Other Places", 
          "Offices"
        ], 
        "shortName": "Tech Startup", 
        "id": "4bf58dd8d48988d125941735", 
        "icon": "https://foursquare.com/img/categories/shops/technology.png"
      }
    ], 
    "likes": {
      "count": 0, 
      "groups": []
    }
  }, 
  "entities": [], 
  "shout": "I'm in your consumers, testing your push API!", 
  "timeZoneOffset": 0, 
  "timeZone": "UTC", 
  "type": "checkin", 
  "id": "4f70a950e5e8e5a7eaa36fff", 
  "createdAt": 1332783440, 
  "user": {
    "photo": "https://is0.4sqi.net/userpix_thumbs/S54EHRPJAHQK0VHP.jpg", 
    "canonicalUrl": "https://foursquare.com/user/1", 
    "firstName": "Jimmy", 
    "lastName": "Foursquare", 
    "homeCity": "New York, NY", 
    "relationship": "self", 
    "gender": "male", 
    "id": "1"
  }
}
"""
class FoursquareHandler(ExternalEventHandler):
    def post(self):
        logging.info('Post arguments = "%s"' % self.request.arguments)
        if 'checkin' in self.request.arguments:
            logging.info('Getting JSON from Foursquare post')
            checkin = json.loads(self.get_argument('checkin'))
            fsqu = checkin['user']
            venue = checkin['venue']
            user = self.getuser(fsqid=fsqu['id'])
            if user is None:
                # TODO: handle unknown users? there really shouldn't be any unknown users...
                pass
            else:
                self.send_event(domain = 'user', name = 'checked_in',
                        user_name = user['username'], venue = json.dumps(venue))

        else:
            pass


class TwilioCallHandler(tornado.web.RequestHandler):
    def handle_call(self):
        print 'Got incomming call from %s' % self.request.arguments['From'][0]
        self.set_header("Content-Type", "text/xml")
        self.set_header("Cache-Control", "no-store")
        self.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n')
        self.write(
        '<Response>'
            '<Say>Hello caller.</Say>'
            '<Gather numDigits="1" action="/twilio/call/get_reminder" method="POST">'
                '<Say>To enter a new reminder, press 1.</Say>'
            '</Gather>'
        '</Response>')

    def post(self):
        self.handle_call()
    
    def get(self):
        self.handle_call()


class TwilioCallGetReminderHandler(tornado.web.RequestHandler):
    def handle_call(self):
        print 'Getting reminder text'
        self.set_header("Content-Type", "text/xml")
        self.set_header("Cache-Control", "no-store")
        self.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n')
        self.write("""
                    <Response>
                        <Say>After the beep, please say the reminder. Press the pound key when finished.</Say>
                        <Record transcribe="true" transcribeCallback="/twilio/call/get_reminder/reminder_recorded" finishOnKey="#" playBeep="true" maxLength="30" action="/twilio/call/get_venue" method="POST"/>
                    </Response>
                   """)
        self.write('Sent response to get reminder text')

    def post(self):
        self.handle_call()

    def get(self):
        self.handle_call()


class TwilioCallGetVenueHandler(tornado.web.RequestHandler):
    def handle_call(self):
        print 'Getting reminder venue'
        self.set_header("Content-Type", "text/xml")
        self.set_header("Cache-Control", "no-store")
        self.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n')
        self.write("""
                    <Response>
                        <Say>After the beep, please say the name of a specifc venue or the type of venue this reminder applies to. Press the pound key when finished.</Say>
                        <Record transcribe="true" transcribeCallback="/twilio/call/get_venue/venue_recorded" finishOnKey="#" playBeep="true" maxLength="30" method="POST"/>
                    </Response>
                   """)
        self.write('Sent response to get venue text')

    def post(self):
        self.handle_call()

    def get(self):
        self.handle_call()


class TwilioCallGotReminderHandler(tornado.web.RequestHandler):
    def handle_call(self):
        reminder_text = self.request.arguments['TranscriptionText'][0]
        logging.info('Reminder text from transcript: %s' % reminder_text)
        logging.info('Finished recording reminder')

    def post(self):
        self.handle_call()

    def get(self):
        self.handle_call()


class TwilioCallGotVenueHandler(tornado.web.RequestHandler):
    def handle_call(self):
        reminder_text = self.request.arguments['TranscriptionText'][0]
        logging.info('Venue from transcript: %s' % reminder_text)
        logging.info('Finished recording venue')

    def post(self):
        self.handle_call()

    def get(self):
        self.handle_call()


class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello')
