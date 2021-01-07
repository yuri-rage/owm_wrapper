from pyowm import OWM
import owm_api_key
from pyowm.utils import timestamps
from geoname import GeoName
import pprint  # TODO: remove this - debug only
from dataclasses import dataclass


@dataclass
class City:
    id: int  # from owm city_id_registry
    name: str
    country: str
    lat: float
    lon: float


owm = OWM(owm_api_key.key)
"""
    create a file in this path called owm_api_key.py
    it only needs to contain one line:
    key = '<your api key>'
    free keys can be generated at https://openweathermap.org
"""


def heading_to_cardinal(heading):
    cardinals = ['North', 'North northeast', 'Northeast', 'East northeast',
                 'East', 'East southeast', 'Southeast', 'South southeast',
                 'South', 'South southwest', 'Southwest', 'West southwest',
                 'West', 'West northwest', 'Northwest', 'North northwest']
    index = round(heading / (360. / len(cardinals)))
    return cardinals[index % len(cardinals)]


def pretty_temp_diff(temp1, temp2):
    diff = temp2 - temp1
    if abs(diff) < 3:
        return 'similar'
    if 2 < diff < 7:
        return 'warmer'
    if diff > 0:
        return 'much warmer'
    if diff > -7:
        return 'cooler'
    return 'much cooler'


def pretty_wind(wind_speed):  # grammatically, return values should follow the words, "with" or "and"
    if wind_speed < 4:
        return 'calm wind'
    if wind_speed < 8:
        return 'a light breeze'
    if wind_speed < 16:
        return 'light wind'
    if wind_speed < 26:
        return 'moderate wind'
    if wind_speed < 41:
        return 'high winds'
    return 'very high winds'


def get_city(city, country=''):
    """
    Note: the GeoName class is US-state preferential, since that's where I live
          that means that it's entirely possible to match a city in a country like Germany (DE), and return
          'Delaware' as the country name (if the country is not explicitly specified in the query terms)
    """
    reg = owm.city_id_registry()
    geo = GeoName(country)

    # try exact match for city and country abbreviation
    city_list = reg.ids_for(city.title(), country=geo.alpha_2, matching='exact')
    if city_list:
        result = city_list[0][0], city_list[0][1], geo.name
    else:
        # try like match for city and country abbreviation
        city_list = reg.ids_for(city, country=geo.alpha_2, matching='like')
        if city_list:
            result = city_list[0][0], city_list[0][1], geo.name
        else:
            # finally, try like match for just city
            city_list = reg.ids_for(city, matching='like')
            if city_list:
                result = city_list[0][0], city_list[0][1], geo.name
            else:
                # I give up!
                return None

    if geo.name is None:  # found a city-only match, get the country
        result = result[0], result[1], GeoName(city_list[0][2]).name
    # this is bass-ackwards, but pyowm does not provide a mechanism to retrieve a complete registry entry
    #   with id, city, country, latitude, and longitude (that I could find)
    #   so, take the result found above and retrieve a location object with lat/lon
    location = reg.locations_for(result[1], geo.alpha_2, 'exact')[0]
    return City(*result, location.lat, location.lon)


def pretty_wx_today(city_name, country_name=None, temp_unit='fahrenheit'):

    city = get_city(city_name, country_name)

    mgr = owm.weather_manager()
    obs = mgr.weather_at_id(city.id).weather
    fcst = mgr.one_call(city.lat, city.lon).forecast_daily[0]
    obs_high = round(obs.temperature(temp_unit)["temp_max"])
    fcst_high = round(fcst.temperature(temp_unit).get('max'))
    if 'gust' in obs.wind():
        gust = f' gusting to {int(obs.wind()["gust"])} knots'
    else:
        gust = ''
    return f'{obs.detailed_status.capitalize()} over {city.name}, {city.country}. ' \
           f'{round(obs.temperature(temp_unit)["temp"])} degrees ' \
           f'with a high of {obs_high} and a low of {round(obs.temperature(temp_unit)["temp_min"])} degrees.\n' \
           f'Currently feels like {round(obs.temperature(temp_unit)["feels_like"])} degrees. ' \
           f'{obs.humidity} percent humidity. ' \
           f'{heading_to_cardinal(obs.wind()["deg"])} wind at {round(obs.wind()["speed"])} knots{gust}.\n' \
           f'{fcst.detailed_status.capitalize()} tomorrow with ' \
           f'{pretty_temp_diff(obs_high, fcst_high)} temperatures ' \
           f'and {pretty_wind(fcst.wind()["speed"])}.'


if __name__ == '__main__':
    """
    mgr = owm.weather_manager()
    city = get_city('lucas', 'texas')
    forecast = mgr.one_call(city.lat, city.lon).forecast_daily[0]
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(forecast.to_dict())
    """

    print(pretty_wx_today('lucas', 'texas'))
