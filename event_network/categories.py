import re
import string
import httplib


regex = re.compile('[%s]' % re.escape(string.punctuation))

def remove_punc(s):
    return regex.sub('', s)


class Category:

    category_map = {}
    fsqr_categories = []

    @classmethod
    def get_category_from_location(cls, category_text):
        # First see if we get an exact match
        if Category.category_map.has_key(category_text):
            Category.category_map[category_text]

        # Now compare case-insensitive and any substring
        lower_text = category_text.lower()
        for k, v in Category.category_map.iteritems():
            if k.lower() in lower_text:
                return v

        lower_text = remove_punc(lower_text)
        for k, v in Category.category_map.iteritems():
            if remove_punc(k.lower()) in lower_text:
                return v

        return None

    @classmethod
    def load_category_aliases(cls):
        file = open('categories.map')
        for line in file:
            line = line.strip()
            if len(line) > 0:
                parts = line.split(':')
                if len(parts) == 2  :
                    category = parts[0]
                    category = category.strip()
                    aliases = parts[1].split(',')
                    #print "%s => %s" % (category, category)
                    Category.category_map[category] = category
                    for alias in aliases:
                        alias = alias.strip()
                        #print "%s => %s" % (alias, category)
                        Category.category_map[alias] = category

    @classmethod
    def load_fsqr_categories(cls):
        connection = httplib.HTTPConnection('api.foursquare.com')
        https://api.foursquare.com/v2/venues/categories?oauth_token=RGM52JFE0XDSLVO1O15BC1TTDEU2XT1RUBCJBXL4QQ1ASUHA&v=20120327

    @classmethod
    def category_matches_location(cls, category, location):
        # See if the location without punctuation contains the category text without punctuation (with differning case)
        if remove_punc(category.lower()) in remove_punc(location.lower()):
            return True

        resolved_category = Category.get_category_from_location(location)
        if not resolved_category:
            return False

        return resolved_category.lower() == category.lower()


Category.load_categories()
