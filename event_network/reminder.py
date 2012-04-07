from categories import *
import requests
import json


class Reminder:

    @classmethod
    def parse(cls, text):
        parts = text.split('@')
        if len(parts) != 2:
            raise Exception('Invalid reminder syntax "%s"' % text)
        item = parts[0].strip()
        location = parts[1].strip()
        return Reminder(None, None, item, location, True)

    def __init__ (self, reminder_id, user_name, item, location, active):
        self._reminder_id = reminder_id
        self._user_name = user_name
        self._item = item
        self._location = location
        self._active = active

    def item(self):
        return self._item

    def location(self):
        return self._location

    def is_active(self):
        return self._active

    def activate(self):
        reminder_map = {"active" : 1}
        requests.put('http://184.169.147.21/%s/reminders/%s' % (self._user_name, self._reminder_id), data=reminder_map)
        self._active = True

    def inactivate(self):
        logging.info('Inactivating reminder %s for user %s' % (self._reminder_id, self._user_name))
        reminder_map = {"active" : 0}
        requests.put('http://184.169.147.21/%s/reminders/%s' % (self._user_name, self._reminder_id), data=reminder_map)
        self._active = False

    def venue_appies_to_reminider(self, venue):
        if self.venue_name_applies_to_location(venue['name']):
            return True
        
        for category in venue['categories']:
            if self.category_applies_to_location(category['shortName']) or self.category_applies_to_location(category['name']):
                return True

        return False

    def venue_name_applies_to_location(self, venue_name):
        venue_name = remove_punc(venue_name.lower())
        location = remove_punc(self._location.lower())

        return venue_name in location or location in venue_name

    def category_applies_to_location(self, category):
        return Category.category_matches_location(category, self._location)

    def assign_to_user(self, user_name):
        if not reminders.has_key(user_name):
            reminders[user_name] = []
        reminders[user_name].append(self)



