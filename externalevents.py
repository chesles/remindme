#!/usr/bin/env python

import tornado.ioloop
import tornado.web

from handlers import external
from conf import settings

application = tornado.web.Application([
    (r'/twilio/sms', external.TwilioHandler),
    (r'/fsq/push', external.FoursquareHandler)
])

if __name__ == '__main__':
    application.listen(8083, ssl_options = settings.ssl_options)
    tornado.ioloop.IOLoop.instance().start()
