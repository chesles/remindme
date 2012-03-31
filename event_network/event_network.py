#!/usr/bin/python


import tornado.ioloop
import tornado.web

import json
import unicodedata

import httplib, urllib

import sms_notification_handler

from user import *
from reminder import *


def ascii(us):
    unicodedata.normalize('NFKD', us).encode('ascii','ignore')

class EventHandler(tornado.web.RequestHandler):
    def post(self, domain, name):
        self.set_header("Content-Type", "text/plain")
        self.write('got event %s:%s\n' % (domain,name))
        print 'got event %s:%s\n' % (domain,name)
        if not self.request.arguments.has_key('from_test_page'):
            self.finish()  # If this event was not received from the test page, call finish here to respond back to the client.  This makes the event processsing asynchronous.
        self.fired(self.request.arguments)
        if self.request.arguments.has_key('from_test_page'):
            self.redirect("/")


class UnknownEventHandler(EventHandler):
    def fired(self, attributes):
        pass


class NewRemniderSentHandler(EventHandler):
    def fired(self, attributes):
        user_name = attributes['user_name'][0]

        print 'Looking for user %s' % user_name
        user = User.get_by_user_name(user_name)
        if not user:
            print 'Error: Unknown user_name "%s"' % user_name
        print 'Found user "%s"' % user_name

        reminder = Reminder.parse(attributes['reminder_text'][0])

        user.add_reminder(reminder)


class UserCheckedInHandler(EventHandler):
    def fired(self, attributes):
        user_name = attributes['user_name'][0]

        print 'Looking for user %s' % user_name
        user = User.get_by_user_name(user_name)
        if not user:
            print 'Error: Unknown user_name "%s"' % user_name
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

        event_map = {"_domain" : "reminder", "_name" : "list_available", "user_name" : user_name, "venue_name" : venue['name'], "reminder_list" : json.dumps(reminder_list)}
        print 'Sending "reminder:list_available" event with attributes "%s"' % json.dumps(event_map)

        # Send the post
        params = urllib.urlencode(event_map)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        connection = httplib.HTTPConnection("localhost", 8080)
        connection.request("POST", "/event/reminder/list_available", params, headers)
        print 'Sent reminder:list_available event'


class ReminderListAvailableHandler(EventHandler):
    def fired(self, attributes):
        print 'Retrieving event attributes'

        user_name = attributes['user_name'][0]
        print 'user_name: %s' % user_name

        venue_name = attributes['venue_name'][0]
        print 'venue_name: "%s"' % venue_name

        reminder_list_str = attributes['reminder_list'][0]
        print 'reminder_list: %s' % reminder_list_str
        reminder_list = json.loads(reminder_list_str)

        # Generate the message to send to the user.
        message = 'While you\'re at "%s" remember to: ' % venue_name
        for i in range(len(reminder_list)):
            message = message + ' %s' % reminder_list[i]
            if i == len(reminder_list) - 1:
                message = message + '.'
            else:
                message = message + ','

        print 'Sending message to user: "%s"' % message

        # Send the messge to the user.
        sms_notification_handler.notify_user(user_name, message)



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

