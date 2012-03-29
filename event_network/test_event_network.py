#!/usr/bin/python


import sys
from event_network import *
from venue import *
from categories import *


venue1_text = """
                {
                        "name": "foursquare HQ",
                        "location": {
                            "address": "East Village",
                            "lat": 40.72809214560253,
                            "lng": -73.99112284183502,
                            "city": "New York",
                            "state": "NY",
                            "postalCode": "10003",
                            "country": "USA"
                        },
                        "categories": [
                            {
                                "shortName": "Tech Startup"
                            }
                        ]
                    }
                """

venue2_text = """
                {
                        "name": "Home Depot",
                        "location": {
                            "address": "885 W Grassland Dr.",
                            "lat": 40.3845805222408,
                            "lng": -111.822398900986	,
                            "city": "Lehi",
                            "state": "UT",
                            "postalCode": "84043",
                            "country": "USA"
                        },
                        "categories": [
                            {
                                "shortName": "Hardware"
                            }
                        ]
                    }
                """


reminder1_item = "get door pulls"
reminder1_location = "home depot"
reminder1 = "%s @  %s " % (reminder1_item, reminder1_location)
bad_reminder = "do something at some place"

def text_parse_venue():
    global venue1_text
    venue = Venue.parse(venue1_text)
    assert venue.name() == "foursquare HQ"
    assert venue.latitude() == 40.72809214560253
    assert venue.longitude() == -73.99112284183502
    assert len(venue.categories()) == 1
    assert 'Tech Startup' in venue.categories()


def test_reminder_parse():
    global reminder1
    reminder = Reminder.parse(reminder1)
    assert reminder.item() == reminder1_item 
    assert reminder.location() == reminder1_location
    try:
        Reminder.parse(bad_reminder)
        assert False    # This line should not execute
    except Exception:
        pass

def test_category_resolution():
    assert Category.resolve('grocery store') == 'Grocery Store'
    assert Category.resolve('SUPERMARKET') == 'Grocery Store'
    assert Category.resolve('book store') == 'Bookstore'
    assert Category.resolve('Home improvement store') == 'Hardware'
    assert Category.resolve("H-om'e impr!ove?m'ent store") == 'Hardware'
    assert Category.resolve('Home CENTER') == 'Hardware'
    assert Category.resolve('Credit uNION') == 'Bank / Financial'
    assert Category.resolve("doctor's") == "Doctor's Office"
    assert Category.resolve("Nursery") == "Garden Center"
    assert Category.resolve("gfkjkgds") == None
    assert Category.resolve("") == None
    assert Category.resolve(" ") == None
    assert Category.resolve("r") == None
    assert Category.resolve("Smith's") == None
    assert Category.resolve("Khol's") == None
    assert Category.resolve("Wlamart") == None

def test_checked_in_event():
    global venue1_text
    checked_in_event_attributes = {"venue" : venue1_text, "user_id" : 1}
    checked_in_handler = UserCheckedInHandler()
    checked_in_handler.fired(checked_in_event_attributes)


def test_main():
    text_parse_venue()
    test_reminder_parse()
    test_category_resolution()
    return 0


if __name__ == '__main__':
    sys.exit(test_main())














