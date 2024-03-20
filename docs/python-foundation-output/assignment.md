# Assignment

Your assignment is to geocode the addresses given below using [GeoPy](https://geopy.readthedocs.io/en/stable/). This assignment is designed to help you practice your coding skills learnt in the course so far.

## Part 1

You have been given a list containing 5 tuples of place names along with their address. You need to use the [Nominatim](https://geopy.readthedocs.io/en/stable/#module-geopy.geocoders) geocoder and obtain the latitude and longitude of each address.


```python
# List of Hurricane Evacuation Centers in New York City with Addresses
# Each item is a tuple with the name of the center and its address
locations = [
    ('Norman Thomas HS (ECF)', '111 E 33rd St, NYC, New York'),
    ('Midtown East Campus', '233 E 56th St, NYC, New York'),
    ('Louis D. Brandeis HS', '145 W 84th St, NYC, New York'),
    ('Martin Luther King, Jr. HS', '122 Amsterdam Avenue, NYC, New York'),
    ('P.S. 48', '4360 Broadway, NYC, New York')
]
```

The expected output should be as follows

```
[('Norman Thomas HS (ECF)', 40.7462177, -73.9809816),
 ('Midtown East Campus', 40.65132465, -73.92421646290632),
 ('Louis D. Brandeis HS', 40.7857432, -73.9742029),
 ('Martin Luther King, Jr. HS', 40.7747751, -73.9853689),
 ('P.S. 48', 40.8532731, -73.9338592)]
```

## Part 2

Get a list of 5 addresses in your city and geocode them.

You can use Nominatim geocoder. Nominatim is based on OpenStreetMap and the it's geocoding quality varies from country to country. You can visit https://openstreetmap.org/ and search for your address. It uses Nominatim geocoder so you can check if your address is suitable for this service.

Many countries of the world do not have structured addresses and use informal or landmark based addresses. There are usually very difficult to geocode accurately. If you are trying to geocode such addresses, your best bet is to truncate the address at the street or locality level.

For example, an address like following will fail to geocode using Nominatim

```
Spatial Thoughts LLP,
FF 105, Aaradhya Complex,
Gala Gymkhana Road, Bopal,
Ahmedabad, India
```

Instead, you may try to geocode the following

```
Gala Gymkhana Road, Bopal, Ahmedabad, India
```


## Part 3

Bonus Assignment (This part is optional)

Use an alternative geocoding service such as HERE/Bing/Google or a country-specific service such as DataBC. Note that most commercial geocoding services will require signing-up for an API key and may also require setting up a billing account.
