from reminder import *


class User:

    def __init__(self, first_name, last_name, fsqr_id, phone_number, email):
        User.user_count = User.user_count + 1
        self._user_id = User.user_count
        self._first_name = first_name
        self._last_name = last_name
        self._fsqr_id = fsqr_id
        self._phone_number = phone_number
        self._email = email

    def user_id(self):
        return self._user_id

    def first_name(self):
        return self._first_name

    def last_name(self):
        return self._last_name

    def fsqr_id(self):
        return self._fsqr_id

    def phone_number(self):
        return self._phone_number

    def email(self):
        return self._email

    def reminders(self):
        return get_reminders_for_user(self._user_id)

    @classmethod
    def get_by_id(cls,user_id):
        for user in User.user_list:
            if user.user_id() == user_id:
                return user
        return None

    user_count = 0

    user_list = []


User.user_list.append(User('Jonatha', 'Ludwig', '20298748', '8016109129', 'jr.ludwig@gmail.com'))



