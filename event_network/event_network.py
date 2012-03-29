import tornado.ioloop
import tornado.web

from user import *
from reminder import *


class EventHandler(tornado.web.RequestHandler):
    def post(self, domain, name):
        self.fired(self, self.request.arguments)


class UnknownEventHandler(EventHandler):
    def fired(self, attributes):
        pass


class UserCheckedInHandler(EventHandler):
    def fired(self, attributes):
        user_id = long(attributes['user_id'][0])
        user = get_user_by_id(user_id)
        if not user:
            raise tornado.web.HTTPError(400, "Unknown user id %d" % user_id)

        location = ""   # TODO: What is this

        # Build a list of reminders that apply to this location
        reminder_list = []
        reminders = user.reminders()
        for reminder in reminders:
            if reminder.is_active() and reminder.applies_to(location):
                reminder_list.append(reminder)
                reminder.inactivate()

        # Raise the ReminderListAvailableHandler event which will notify the user.


class NewRemniderSentHandler(EventHandler):
    def fired(self, attributes):
        user_id = long(attributes['user_id'][0])
        user = get_user_by_id(user_id)
        if not user:
            raise tornado.web.HTTPError(400, "Unknown user id %d" % user_id)


class ReminderListAvailableHandler(EventHandler):
    def fired(self, attributes):
        user_id = long(attributes['user_id'][0])
        user = get_user_by_id(user_id)
        if not user:
            raise tornado.web.HTTPError(400, "Unknown user id %d" % user_id)
        phone_number = user.phone_number()


application = tornado.web.Application([
    (r"/event/(user)/(checked_in)", UserCheckedInHandler),
    (r"/event/(reminder)/(new)", NewRemniderSentHandler),
    (r"/event/(reminder)/(list_available)", ReminderListAvailableHandler),
    (r"/event/(\w+)/(\w+)", UnknownEventHandler),
])


if __name__ == "__main__":
    try:
        application.listen(8080)
        tornado.ioloop.IOLoop.instance().start()
    finally:
        logFile.close()

