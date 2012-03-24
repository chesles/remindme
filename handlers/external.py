import tornado.web

class ExternalEventHandler(tornado.web.RequestHandler):
    # implement common functionality here
    pass

class TwilioHandler(ExternalEventHandler):
    def post(self):
        # package data into an internal event and forward it
        pass

class FoursquareHandler(ExternalEventHandler):
    def post(self):
        # package data into an internal event and forward it
        pass
