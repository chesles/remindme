from reminder import *
import requests
import json


class User:

    def __init__(self, user_name, fsqr_id, phone_number):
        self._user_name = user_name
        self._fsqr_id = fsqr_id
        self._phone_number = phone_number

    def user_name(self):
        return self._user_name

    def fsqr_id(self):
        return self._fsqr_id

    def phone_number(self):
        return self._phone_number

    def reminders(self):
        response = requests.get("http://184.169.147.21/%s/reminders" % self._user_name)
        reminder_list = json.loads(response.text)
        return [Reminder(reminder['_id'], self._user_name, reminder['text'], reminder['location'], False if reminder['active'] == "0" else True) for reminder in reminder_list]

    def add_reminder(self, reminder):
        reminder_map = {"text" : reminder.item(), "location" : reminder.location(), "active" : 1 if reminder.is_active() else 0}
        requests.post('http://184.169.147.21/%s/reminders' % self._user_name, data=reminder_map)

    @classmethod
    def get_by_user_name(cls,user_name):
        response = requests.get("http://184.169.147.21/%s" % user_name)
        user_list = json.loads(response.text)
        if len(user_list) == 0:
            return None

        user = user_list[0]
        return User(user['username'], user['fsqid'], user['phone'])

    @classmethod
    def get_all_users(cls):
        response = requests.get("http://184.169.147.21/")
        user_list = json.loads(response.text)
        return [User(user['username'], user['fsqid'], user['phone']) for user in user_list]


