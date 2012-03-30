#!/usr/bin/python


import tornado.ioloop
import tornado.web

import json
from twilio.rest import TwilioRestClient    # TODO: Move this into an SMS nofitication handler
import unicodedata

from user import *
from reminder import *


def ascii(us):
    unicodedata.normalize('NFKD', us).encode('ascii','ignore')

class EventHandler(tornado.web.RequestHandler):
    def post(self, domain, name):
        self.set_header("Content-Type", "text/plain")
        self.write('got event %s:%s\n' % (domain,name))
        if not self.request.arguments.has_key('from_test_page'):
            self.finish()  # Comment this line out for debugging
        self.fired(self.request.arguments)
        if self.request.arguments.has_key('from_test_page'):
            self.redirect("/")


class UnknownEventHandler(EventHandler):
    def fired(self, attributes):
        pass


class UserCheckedInHandler(EventHandler):
    def fired(self, attributes):
        user_name = attributes['user_name'][0]

        print 'Looking for user %s' % user_name
        user = User.get_by_user_name(user_name)
        if not user:
            raise tornado.web.HTTPError(400, "Unknown user_name %s" % user_name)
        print 'Found user "%s"' % user_name

        venue_str = attributes['venue'][0]
        venue = json.loads(venue_str)

        # Build a list of reminders that apply to this location
        reminder_list = []
        reminders = user.reminders()
        for reminder in reminders:
            if reminder.is_active() and reminder.venue_appies_to_reminider(venue):
                reminder_list.append(reminder.item())
                reminder.inactivate()

        # Raise the ReminderListAvailableHandler event which will notify the user.
        if len(reminder_list) == 0:
            print 'No reminders apply to venue "%s"' % venue['name']
        else:
            print 'The following reminders apply to venue "%s":' % venue['name']
            for reminder in reminder_list:
                print '  %s' % reminder

        event_map = {"user_name" : user_name, "venue" : venue, "reminder_list" : reminder_list}
        print 'Sending "reminder:list_available" event with attributes "%s"' % json.dumps(event_map)
        message = 'While you\'re at "%s" be sure to: ' % venue['name']
        for i in range(len(reminder_list)):
            message = message + ' %s' % reminder_list[i]
            if i == len(reminder_list) - 1:
                message = message + '.'
            else:
                message = message + ','

        # TODO: Move this into an SMS nofitication handler
        client = TwilioRestClient('AC7de62158f793498e846749097dc57f6e', '8e59de93a11b2883a5929189edfc9b7b')
        sms_message = client.sms.messages.create(from_="+18016580216", to=user.phone_number(), body=message)


class NewRemniderSentHandler(EventHandler):
    def fired(self, attributes):
        user_name = attributes['user_name'][0]

        print 'Looking for user %s' % user_name
        user = User.get_by_user_name(user_name)
        if not user:
            raise tornado.web.HTTPError(400, "Unknown user_name %s" % user_name)
        print 'Found user "%s"' % user_name

        reminder = Reminder.parse(attributes['reminder_text'][0])

        user.add_reminder(reminder)


class ReminderListAvailableHandler(EventHandler):
    def fired(self, attributes):
        user_name = attributes['user_name'][0]

        print 'Looking for user %s' % user_name
        user = User.get_by_user_name(user_name)
        if not user:
            raise tornado.web.HTTPError(400, "Unknown user_name %s" % user_name)
        print 'Found user "%s"' % user_name

        venue = attributes['venue'][0]
        reminder_list = attributes['reminder_list'][0]

        venue = json.loads(venue)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        user = User.get_by_user_name('jrl')
        self.render("index.html", reminders=user.reminders())

application = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/event/(user)/(checked_in)", UserCheckedInHandler),
    (r"/event/(user)/(new_reminder)", NewRemniderSentHandler),
    (r"/event/(reminder)/(list_available)", ReminderListAvailableHandler),
    (r"/event/(\w+)/(\w+)", UnknownEventHandler),
])


if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

