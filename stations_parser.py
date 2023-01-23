import json
from math import radians, cos, sin, asin
import sys
from slugify import slugify


def distance_haversine(point_1: tuple, point_2: tuple):
    d_earth = 2.0 * 6372.8
    lat1, long1 = tuple(radians(c) for c in point_1)
    lat2, long2 = tuple(radians(c) for c in point_2)
    d = sin((lat2 - lat1) / 2.0) ** 2.0 + cos(lat1) * cos(lat2) * sin(
        (long2 - long1) / 2.0) ** 2.0
    return d_earth * asin(d ** 0.5)


def find_nearest(point_1: tuple, points: dict):
    dists = {p: distance_haversine(point_1, points[p]) for p in points}
    name, dist = min(dists.items(), key=lambda d: d[1])
    return {'name': name, 'distance': dist,
            'dist_coef': 3 if dist <= 1.0 else 2 if dist < 2.0 else 1}


metro_points = {
    #'Новокосино': (55.745113, 37.864052),
    #'Перово': (55.75098, 37.78422),
    'Ховрино': (55.8777, 37.4877),
    }

# print(type(metro_points))
# print(type(metro_points['Ховрино']))
# sys.exit(0)
point_1 = (55.7538337, 37.6211812) 
#Координаты Красной площади. Широта: 55.7538337, Долгота: 37.6211812.
#print(find_nearest(point_1, metro_points))
# {'name': 'Ховрино', 'distance': 15.823760672698684, 'dist_coef': 1}
#sys.exit(0)
# Opening JSON file
f = open('metro_stations_msk.json', encoding='utf-8', errors='ignore')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
stats = {}

# Iterating through the json
n = 0
for idx, stat in enumerate(data['lines']):
    #print('------', i['name'])
    for station in stat['stations']:
        stations_map = {}
        #stats[station['name']] = n
        #print('station: ', station['name'], n)
        #n += 1
        #print('station: ', station['name'], station['lat'], ',', station['lng'])
        stations_map[station['name']] = (float(station['lat']), float(station['lng']))
        print(find_nearest(point_1, stations_map))
        #metro_points = {float(station['lat']), float(station['lng'])}

        # slug = slugify(station['name'], separator='_')
        # rez = '<option value="{}">{}</option>'.format(slug, station['name'])
        # print(rez)

print(stations_map)    
  
# Closing file
f.close()

#print(stations_map)