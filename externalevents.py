#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.options

import logging
import string
import os
import sys

tornado.options.parse_command_line()

exec_dir = string.join(sys.argv[0].split('/')[:-1], '/')

logging.info('Changing working dir to %s ' % exec_dir)
os.chdir(exec_dir)
logging.info('Working dir is %s' % os.getcwd())

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


def main():
    logging.info('Starting External Events server')
    application.listen(443, ssl_options = settings.ssl_options)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
