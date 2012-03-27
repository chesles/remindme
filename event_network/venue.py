import json


class Venue:
    def __init__(self, venue_attributes):
        self.attributes = venue_attributes
        self._name = venue_attributes['name']
        self._lat = float(venue_attributes['location']['lat'])
        self._long = float(venue_attributes['location']['lng'])
        self._categories = [cat['shortName'] for cat in venue_attributes['categories']]

    @classmethod
    def parse(cls, text):
        venue_attributes = json.loads(text)
        return Venue(venue_attributes)
    
    def name(self):
        return self._name

    def latitude(self):
        return self._lat

    def longitude(self):
        return self._long

    def categories(self):
        return self._categories

