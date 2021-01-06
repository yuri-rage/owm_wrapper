## OWM Wrapper

OpenWeatherMap (https://openweathermap.org/) provides an API for retrieving up to date weather data based on city or lat/lon lookups.

The pyowm library provides some basic convenience methods to access the API, but it only generates raw data (usually in the form of dictionaries based on JSON-ified data returned from web queries).

This wrapper uses pyowm to gather weather information and return plain English results geared toward usage in text-to-speech applications.