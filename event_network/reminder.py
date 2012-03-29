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


reminders = {1 : [Reminder('Get door pulls for pantry', 'Home improvement store')]}


def get_reminders_for_user(user_id):
    if reminders.has_key(user_id):
        return reminders[user_id]
    return []
