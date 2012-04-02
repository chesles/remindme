#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.options

import logging

tornado.options.parse_command_line()

from handlers import external
from conf import settings

application = tornado.web.Application([
    (r'/twilio/sms', external.TwilioHandler),
    (r'/fsq/push', external.FoursquareHandler),
    (r'/twilio/call', external.TwilioCallHandler),
    (r'/twilio/call/new_reminder', external.TwilioCallNewReminderHandler),
    (r'/twilio/call/new_reminder/reminder_recorded', external.TwilioCallNewReminderGotReminderHandler),
    (r'/twilio/call/get_venue/venue_recorded', external.TwilioCallNewReminderGotVenueHandler),
    (r'/', external.RootHandler),
])

if __name__ == '__main__':
    logging.info('Starting External Events server')
    application.listen(8083, ssl_options = settings.ssl_options)
    tornado.ioloop.IOLoop.instance().start()
