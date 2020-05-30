 #!/usr/bin/env python
import csv
import os
from geopy import distance

home_dir = os.path.expanduser('~')

input_filename = 'worldcities.csv'
input_dir = 'Downloads/python_foundation/'
data_pkg_path = 'Downloads/python_foundation/'
input_path = os.path.join(home_dir, data_pkg_path, input_filename)
output_filename = 'cities_distance.csv'
output_dir = 'Downloads'
output_path = os.path.join(home_dir, output_dir, output_filename)

home_city = 'Bengaluru'
home_country = 'India'

with open(input_path, 'r') as input_file:
    csv_reader = csv.DictReader(input_file)
    for row in csv_reader:
        if row['city_ascii'] == home_city:
            home_city_coordinates = (row['lat'], row['lng'])
            break

with open(output_path, mode='w') as output_file:
    fieldnames = ['city', 'distance_from_home']
    csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    csv_writer.writeheader()

    with open(input_path, 'r') as input_file:
        csv_reader = csv.DictReader(input_file)
        for row in csv_reader:
            if (row['country'] == home_country and
                row['city_ascii'] != home_city):
                city_coordinates = (row['lat'], row['lng'])
                city_distance = distance.geodesic(
                    city_coordinates, home_city_coordinates).km
                csv_writer.writerow(
                    {'city': row['city_ascii'],
                     'distance_from_home': city_distance}
                )

print('Successfully written output file at {}'.format(output_path))