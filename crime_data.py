#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Names:Zhecheng Li
Program: Crime and Border project
Description: Extract data from wikipedia about cities
            Calculate correlation between crime rate and distance to border
Last Modified: 02 Feb 2019
"""
from bs4 import BeautifulSoup
import urllib
import os
import csv
import math
import scipy

def getURL(link):
    wikipedia = 'https://en.wikipedia.org'
    return wikipedia + link

def getFilename(link):
    filename = link.rsplit('/', 1) #split 1 from the right, city name is last item in list
    filename = filename[-1].split(',', 1) #split state from city name
    filename = '../data/' + filename[0] + '.html' #city name is first item in list, add html extension
    return filename

def getDocument(link):
    filename = getFilename(link)
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            file_r = file.read()
        soup = BeautifulSoup(file_r, 'lxml')
    else:
        url = getURL(link)
        with urllib.request.urlopen(url) as source:
            soup = BeautifulSoup(source, 'lxml')
        urllib.request.urlretrieve(url, filename)
    return soup

def getSmallestDistance(city_link, borders):
    soup = getDocument(city_link)
    coordinates = (soup.find('span', class_='geo').text).split(';')
    x_lat = float(coordinates[0])
    x_lon = float(coordinates[1])
    distances = [greatCircleDistance(x_lat, x_lon, y['lat'], y['lon']) for y in borders]
    return(min(distances))

def greatCircleDistance(x_lat, x_lon, y_lat, y_lon):
    EARTH_RADIUS = 6367
    RADIANS = math.pi/180
    lat = (x_lat * RADIANS) - (y_lat * RADIANS)
    lon = (x_lon * RADIANS) - (y_lon * RADIANS)
    distance = ((math.sin((lat)/2))**2 + math.cos(x_lat * RADIANS) * 
                math.cos(y_lat * RADIANS) * (math.sin((lon)/2))**2)
    distance = 2 * math.atan2(math.sqrt(distance), math.sqrt(1-distance))
    return EARTH_RADIUS * distance

DATA_PATH = '../data'
LIST_LINK = '/wiki/List_of_United_States_cities_by_crime_rate'

#create directory if does not exist
if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)

#list of border's latitude and longitude
borders = [{'name':'San Diego', 'lat':32.71500, 'lon': -117.16250},
           {'name':'Yuma', 'lat':32.69222, 'lon': -114.61528},
           {'name':'Tucson', 'lat':32.22167, 'lon': -110.92639},
           {'name':'El Paso', 'lat':31.7592056, 'lon': -106.4901750},
           {'name':'Laredo', 'lat':27.52444, 'lon': -99.49056},
           {'name':'Del Rio', 'lat':29.370833, 'lon': -100.89583},
           {'name':'Brownsville', 'lat':25.93028, 'lon': -97.48444}]

#get data and create list
city_list = list()
count = 0
soup = getDocument(LIST_LINK)
print('Retrieving Data...')
for data in soup.find('table', class_='wikitable').find_all('td'):
    if count == 1 and data.text != 'Anchorage':
        city_name = data.text.rstrip('0123456789*')
        smallest = round(getSmallestDistance(data.a['href'], borders), 4)
    elif count == 3 and city_name != 'Anchorage':
        crime_rate = float(data.text)
        city = {'city':city_name, 'crime rate':crime_rate, 'distance':smallest}
        city_list.append(city)
        print('Got: ' + city_name)
    elif count == 13:
        count = 0
    count += 1
print('Done')

print('Writing CSV file...')
with open('../report/crime_data.csv', 'w') as csvfile:
    fields = ['city', 'crime rate', 'distance']
    file_w = csv.DictWriter(csvfile, fieldnames = fields)
    file_w.writeheader()
    file_w.writerows(city_list)
print('Done')

#Print Correlation
smallestDistance=[]
crimeRate=[]
for city in city_list:
    smallestDistance.append(city['distance'])
    crimeRate.append(city['crime rate'])

print('\nThe coefficient of correlation is: ')
print(scipy.corrcoef(smallestDistance, crimeRate)[0][1])