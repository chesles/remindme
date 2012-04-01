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
        return Reminder.get_reminders_for_user(self._user_name)

    def add_reminder(self, reminder):
        reminder.assign_to_user(self._user_name)

    @classmethod
    def get_by_user_name(cls,user_name):
        response = requests.get("http://localhost:8082/%s" % user_name)
        user_list = json.loads(response.text)
        if len(user_list) == 0:
            return None

        user = user_list[0]
        return User(user['username'], user['fsqid'], user['phone'])

    @classmethod
    def get_all_users(cls):
        response = requests.get("http://localhost:8082/")
        user_list = json.loads(response.text)
        return [User(user['username'], user['fsqid'], user['phone']) for user in user_list]


