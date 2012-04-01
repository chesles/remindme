from categories import *


class Reminder:

    reminder_count = 0

    @classmethod
    def parse(cls, text):
        parts = text.split('@')
        if len(parts) != 2:
            raise Exception('Invalid reminder syntax "%s"' % text)
        item = parts[0].strip()
        location = parts[1].strip()
        return Reminder(item, location)

    def __init__ (self, item, location):
        Reminder.reminder_count = Reminder.reminder_count + 1
        self._reminder_id = Reminder.reminder_count
        self._item = item
        self._location = location
        self._active = True

    def reminder_id(self):
        return self._reminder_id

    def item(self):
        return self._item

    def location(self):
        return self._location

    def applies_to(self, location):
        return True

    def is_active(self):
        return self._active

    def activate(self):
        self._active = True

    def inactivate(self):
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


    @classmethod
    def get_reminders_for_user(cls, user_name):
        if reminders.has_key(user_name):
            return reminders[user_name]
        return []    

reminders = {'jrl' : [Reminder('get pulls for pantry door', 'a home improvement store')],
             'bob' : [Reminder('get eggs', 'smiths')]}



