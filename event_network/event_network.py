#!/usr/bin/python


import tornado.ioloop
import tornado.web
import tornado.options
import logging
import json
import unicodedata
import httplib, urllib
import requests

tornado.options.parse_command_line()


import sms_notification_handler
from user import *
from reminder import *


def ascii(us):
    unicodedata.normalize('NFKD', us).encode('ascii','ignore')

class EventHandler(tornado.web.RequestHandler):
    def post(self, domain, name):
        self.set_header("Content-Type", "text/plain")
        self.write('OK\n')

        logging.info('EventHandler.post: ===============')  
        logging.info('EventHandler.post: Got event %s:%s' % (domain,name))

        #if not self.request.arguments.has_key('from_test_page'):
        #    self.finish()  # If this event was not received from the test page, call finish here to respond back to the client.  This makes the event processsing asynchronous.

        try:
            self.fired(self.request.arguments)
        finally:
            #if self.request.arguments.has_key('from_test_page'):
            #    self.redirect("/")  # If this came from the test page, redirect back to the test page
            logging.info('EventHandler.post: ---------------')


class UnknownEventHandler(EventHandler):
    def fired(self, attributes):
        pass


class NewRemniderSentHandler(EventHandler):
    def fired(self, attributes):
        user_name = attributes['user_name'][0]

        logging.info('NewRemniderSentHandler.post: Looking for user %s' % user_name)
        user = User.get_by_user_name(user_name)
        if not user:
            logging.error('NewRemniderSentHandler.post: Unknown user_name "%s"' % user_name)
        logging.info('NewRemniderSentHandler.post: Found user "%s"' % user_name)

        reminder = Reminder.parse(attributes['reminder_text'][0])

        logging.info('Adding reminder "%s" @ "%s" to user %s' % (reminder.item(), reminder.location(), user.user_name()))
        user.add_reminder(reminder)


class UserCheckedInHandler(EventHandler):
    def fired(self, attributes):
        user_name = attributes['user_name'][0]

        logging.info('UserCheckedInHandler.fired: Looking for user %s' % user_name)
        user = User.get_by_user_name(user_name)
        if not user:
            logging.error('UserCheckedInHandler.fired: Unknown user_name "%s"' % user_name)
        logging.info('UserCheckedInHandler.fired: Found user "%s"' % user_name)

        venue_str = attributes['venue'][0]
        venue = json.loads(venue_str)

        # Build a list of reminders that apply to this location
        logging.info('UserCheckedInHandler.fired: Looking for reminders for user %s that apply to venue "%s"' % (user.user_name(), venue['name']))
        reminder_list = []
        reminders = user.reminders()
        for reminder in reminders:
            logging.debug('UserCheckedInHandler.fired:   Examining reminder "%s" @ "%s"' % (reminder.item(), reminder.location()))
            if not reminder.is_active():
                logging.debug('UserCheckedInHandler.fired:     Skipping reminder "%s" @ "%s" because it is not active' % (reminder.item(), reminder.location()))
                continue
            if reminder.venue_appies_to_reminider(venue):
                logging.debug('UserCheckedInHandler.fired:     Reminder "%s" @ "%s" applies to venue "%s"' % (reminder.item(), reminder.location(), venue['name']))
                reminder_list.append(reminder.item())
                reminder.inactivate()
            else:
                logging.debug('UserCheckedInHandler.fired:     Reminder "%s" @ "%s" does not apply to venue "%s"' % (reminder.item(), reminder.location(), venue['name']))

        # Raise the ReminderListAvailableHandler event which will notify the user.
        if len(reminder_list) == 0:
            logging.info('UserCheckedInHandler.fired: No reminders apply to venue "%s" not sending user a reminder notification' % venue['name'])
            return
        else:
            logging.info('UserCheckedInHandler.fired: Reminders were found that apply to venue "%s":' % venue['name'])
            logging.debug('UserCheckedInHandler.fired: The following reminders apply to venue "%s":' % venue['name'])
            for reminder in reminder_list:
                logging.debug('UserCheckedInHandler.fired:   %s' % reminder)

        event_map = {"_domain" : "reminder", "_name" : "list_available", "user_name" : user_name, "venue_name" : venue['name'], "reminder_list" : json.dumps(reminder_list)}
        logging.info('UserCheckedInHandler.fired: Sending "reminder:list_available" event with attributes "%s"' % json.dumps(event_map))

        # Send the post
        requests.post('http://localhost:8080/event/reminder/list_available', data=event_map)
        #params = urllib.urlencode(event_map)
        #headers = {"Content-type": "application/x-www-form-urlencoded",
        #           "Accept": "text/plain"}
        #connection = httplib.HTTPConnection("localhost", 8080)
        #connection.request("POST", "/event/reminder/list_available", params, headers)
        #connection.getresponse()
        logging.info('UserCheckedInHandler.fired: Sent reminder:list_available event')


class ReminderListAvailableHandler(EventHandler):
    def fired(self, attributes):
        logging.info('ReminderListAvailableHandler.fired: Retrieving event attributes')

        user_name = attributes['user_name'][0]
        logging.info('ReminderListAvailableHandler.fired: user_name: %s' % user_name)

        venue_name = attributes['venue_name'][0]
        logging.info('ReminderListAvailableHandler.fired: venue_name: "%s"' % venue_name)

        reminder_list_str = attributes['reminder_list'][0]
        logging.info('ReminderListAvailableHandler.fired: reminder_list: %s' % reminder_list_str)
        reminder_list = json.loads(reminder_list_str)

        # Generate the message to send to the user.
        message = 'While you\'re at "%s" remember to: ' % venue_name
        for i in range(len(reminder_list)):
            message = message + ' %s' % reminder_list[i]
            if i == len(reminder_list) - 1:
                message = message + '.'
            else:
                message = message + ','

        logging.info('ReminderListAvailableHandler.fired: Sending message to user %s: "%s"' % (message, user_name))

        # Send the messge to the user.
        sms_notification_handler.notify_user(user_name, message)



class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        user = User.get_by_user_name('jrl')
        self.render("index.html", users=User.get_all_users())


class LogHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.render("event_network.log")


def main():
    logging.info("main: starting torando web server")

    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/log", LogHandler),
        (r"/event/(user)/(checked_in)", UserCheckedInHandler),
        (r"/event/(user)/(new_reminder)", NewRemniderSentHandler),
        (r"/event/(reminder)/(list_available)", ReminderListAvailableHandler),
        (r"/event/(\w+)/(\w+)", UnknownEventHandler),
    ])

    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
