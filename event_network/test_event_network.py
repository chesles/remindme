#!/usr/bin/python


import sys
import json
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
                                "name": "Tech Startup",
                                "shortName": "Tech Startup"
                            }
                        ]
                    }
                """

home_depot_text = """
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
                                "name": "Hardware Store",
                                "shortName": "Hardware"
                            }
                        ]
                    }
                """

smiths_text =   """
                {
                    "id":"4b53b968f964a52045a927e3",
                    "name":"Smith's Marketplace",
                    "contact":{
                       "phone":"8013416500",
                       "formattedPhone":"(801) 341-6500"
                    },
                    "location":{
                       "address":"1550 E 3500 N",
                       "lat":40.43029865281793,
                       "lng":-111.82464688468383,
                       "distance":1848,
                       "postalCode":"84043",
                       "city":"Lehi",
                       "state":"UT",
                       "country":"United States"
                    },
                    "categories":[
                       {
                          "id":"4bf58dd8d48988d118951735",
                          "name":"Grocery or Supermarket",
                          "pluralName":"Grocery or Supermarkets",
                          "shortName":"Grocery Store",
                          "icon":{
                             "prefix":"https:\/\/foursquare.com\/img\/categories\/shops\/food_grocery_",
                             "sizes":[
                                32,
                                44,
                                64,
                                88,
                                256
                             ],
                             "name":".png"
                          },
                          "primary":true
                       }
                    ],
                    "verified":false,
                    "stats":{
                       "checkinsCount":1261,
                       "usersCount":268,
                       "tipCount":12
                    },
                    "specials":{
                       "count":0,
                       "items":[
        
                       ]
                    },
                    "hereNow":{
                       "count":2
                    }
                 }
                 """

uccu_text =     """
                {
                    "id":"4f236b54e4b01dc94a979dde",
                    "name":"Utah Community Credit Union",
                    "contact":{
        
                    },
                    "location":{
                       "address":"3281 N 1120 E",
                       "lat":40.42956610259513,
                       "lng":-111.83222166628705,
                       "distance":1702,
                       "postalCode":"84043",
                       "city":"Lehi",
                       "state":"UT",
                       "country":"United States"
                    },
                    "categories":[
                       {
                          "id":"4bf58dd8d48988d10a951735",
                          "name":"Bank",
                          "pluralName":"Banks",
                          "shortName":"Bank \/ Financial",
                          "icon":{
                             "prefix":"https:\/\/foursquare.com\/img\/categories\/shops\/financial_",
                             "sizes":[
                                32,
                                44,
                                64,
                                88,
                                256
                             ],
                             "name":".png"
                          },
                          "primary":true
                       }
                    ],
                    "verified":false,
                    "stats":{
                       "checkinsCount":21,
                       "usersCount":6,
                       "tipCount":1
                    },
                    "specials":{
                       "count":0,
                       "items":[
        
                       ]
                    },
                    "hereNow":{
                       "count":0
                    }
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
    assert Category.get_category_from_location('grocery store') == 'Grocery Store'
    assert Category.get_category_from_location('SUPERMARKET') == 'Grocery Store'
    assert Category.get_category_from_location('book store') == 'Bookstore'
    assert Category.get_category_from_location('Home improvement store') == 'Hardware'
    assert Category.get_category_from_location("H-om'e impr!ove?m'ent store") == 'Hardware'
    assert Category.get_category_from_location('Home CENTER') == 'Hardware'
    assert Category.get_category_from_location('Credit uNION') == 'Bank / Financial'
    assert Category.get_category_from_location("doctor's") == "Doctor's Office"
    assert Category.get_category_from_location("Nursery") == "Garden Center"
    assert Category.get_category_from_location("gfkjkgds") == None
    assert Category.get_category_from_location("") == None
    assert Category.get_category_from_location(" ") == None
    assert Category.get_category_from_location("r") == None
    assert Category.get_category_from_location("Smith's") == None
    assert Category.get_category_from_location("Khol's") == None
    assert Category.get_category_from_location("Wlamart") == None
    assert Category.get_category_from_location('The Grocery Store') == 'Grocery Store'
    assert Category.get_category_from_location('the grocery store') == 'Grocery Store'
    assert Category.get_category_from_location('the dentist') == "Dentist's Office"

def test_category_to_location_matching():
    assert Category.category_matches_location('Bank / Financial', 'the Credit uNION') == True
    assert Category.category_matches_location("Hardware", 'any Home improvement store') == True
    assert Category.category_matches_location("Doctor's Office", 'the doctors') == True
    assert Category.category_matches_location('Grocery Store', "Smith's") == False

def test_category_to_reminder_matching():
    r = Reminder.parse("get door pulls @ a home improvement store")
    assert r.category_applies_to_location("Hardware") == True

    r = Reminder.parse("get milk @ a the grocery store")
    assert r.category_applies_to_location("Grocery Store") == True

    r = Reminder.parse("order new checks @ a the credit union")
    assert r.category_applies_to_location("Bank / Financial") == True

    r = Reminder.parse("request a perscription refill @ a the doctor's")
    assert r.category_applies_to_location("Doctor's Office") == True

def test_venue_to_reminder_matching():
    r = Reminder.parse("get eggs @ smiths")
    assert r.venue_name_applies_to_location("Smith's Food & Drug") == True

    r = Reminder.parse("get a new shirt @ kohls")
    assert r.venue_name_applies_to_location("Kohl's") == True

    r = Reminder.parse("order new checks @ zions")
    assert r.venue_name_applies_to_location("Zion's First National Bank") == True

def test_checkin_location_applies_to_reminders():
    eggs_reminder = Reminder.parse("get eggs @ smiths")
    shirt_reminder = Reminder.parse("get a new shirt @ kohls")
    checks_reminder = Reminder.parse("order new checks @ zions")
    door_pull_reminder = Reminder.parse("get door pulls @ a home improvement store")
    milk_reminder = Reminder.parse("get milk @ a the grocery store")
    cu_checks_reminder = Reminder.parse("order new checks @ the credit union")
    door_knob_reminder = Reminder.parse("get new door knob @ home depot")

    home_depot_location = json.loads(home_depot_text)
    smiths_location = json.loads(smiths_text)
    uccu_location = json.loads(uccu_text)

    assert eggs_reminder.venue_appies_to_reminider(home_depot_location) == False
    assert shirt_reminder.venue_appies_to_reminider(home_depot_location) == False
    assert checks_reminder.venue_appies_to_reminider(home_depot_location) == False
    assert door_pull_reminder.venue_appies_to_reminider(home_depot_location) == True
    assert milk_reminder.venue_appies_to_reminider(home_depot_location) == False
    assert cu_checks_reminder.venue_appies_to_reminider(home_depot_location) == False
    assert door_knob_reminder.venue_appies_to_reminider(home_depot_location) == True

    assert eggs_reminder.venue_appies_to_reminider(smiths_location) == True
    assert shirt_reminder.venue_appies_to_reminider(smiths_location) == False
    assert checks_reminder.venue_appies_to_reminider(smiths_location) == False
    assert door_pull_reminder.venue_appies_to_reminider(smiths_location) == False
    assert milk_reminder.venue_appies_to_reminider(smiths_location) == True
    assert cu_checks_reminder.venue_appies_to_reminider(smiths_location) == False
    assert door_knob_reminder.venue_appies_to_reminider(smiths_location) == False

    assert eggs_reminder.venue_appies_to_reminider(uccu_location) == False
    assert shirt_reminder.venue_appies_to_reminider(uccu_location) == False
    assert checks_reminder.venue_appies_to_reminider(uccu_location) == False
    assert door_pull_reminder.venue_appies_to_reminider(uccu_location) == False
    assert milk_reminder.venue_appies_to_reminider(uccu_location) == False
    assert cu_checks_reminder.venue_appies_to_reminider(uccu_location) == True
    assert door_knob_reminder.venue_appies_to_reminider(uccu_location) == False


def test_main():
    text_parse_venue()
    test_reminder_parse()
    test_category_resolution()
    test_category_to_location_matching()
    test_category_to_reminder_matching()
    test_venue_to_reminder_matching()
    test_checkin_location_applies_to_reminders()
    return 0


if __name__ == '__main__':
    sys.exit(test_main())














