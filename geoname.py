from pycountry import countries  # pip install pycountry
from re import search

us_state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'American Samoa': 'AS', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
    'Florida': 'FL', 'Georgia': 'GA', 'Guam': 'GU', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY',
    'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI',
    'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
    'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Northern Mariana Islands': 'MP', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Puerto Rico': 'PR', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virgin Islands': 'VI', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))


def geo_name_lookup(query):
    name = None
    alpha_2 = None
    try:
        query = query.title()
        alpha_2 = us_state_abbrev[query]
        name = query
    except KeyError:
        d_country = countries.get(name=query)
        if d_country:
            alpha_2 = d_country.alpha_2
            name = d_country.name
        else:
            try:
                d_country = countries.search_fuzzy(query)
                alpha_2 = d_country[0].alpha_2
                name = d_country[0].name
            except LookupError:
                alpha_2 = None
    return name, alpha_2


def geo_alpha_2_lookup(query):
    name = None
    alpha_2 = None
    try:
        query = query.upper()
        name = abbrev_us_state[query]
        alpha_2 = query
    except KeyError:
        d_country = countries.get(alpha_2=query)
        if d_country:
            alpha_2 = d_country.alpha_2
            name = d_country.name
    return name, alpha_2


class GeoName:
    """
    look up country/state names and two letter abbreviations
    openweathermap treats US state abbreviations the same is ISO3166 country codes
    so, this class prefers state abbreviations over ISO3166 country codes (ethnocentrism!)
    unfortunately, that means that ambiguous reverse lookups will return a US state instead of a country
        with the same 2-letter code (e.g., DE=Delaware (not Germany) and AL=Alabama (not Albania)
    -- yuri - Jan 2020
    """

    def __init__(self, query=None):
        self.alpha_2 = None
        self.name = None
        if query is None:
            return

        if search('^[A-Z]{2}$', query):
            self.name, self.alpha_2 = geo_alpha_2_lookup(query)
        else:
            self.name, self.alpha_2 = geo_name_lookup(query)
