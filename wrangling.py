
# File : wrangling.py
# Date : 12/23/2016
# Owner : Rahul Daware
# Description : This file contains code implementation for all data extraction, cleaning and 
# 				JSON generation. This code is a part of Data Wrangling with MongoDB project.

import xml.etree.cElementTree as ET
from collections import defaultdict
import codecs
import json
import pprint
import re

# Required regex
housenumber = re.compile(r'^addr:housenumber')
name = re.compile(r'^addr:name')

#Dictionaries for count related methods
streetcount_suffix = {}
streetcount_prefix = {}
city_list = {}
postcode = {}

# This function will take the XML element, extract necessary information,
# generate a JSON object and return it back
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['id'] = element.attrib['id']
        node['type'] = element.tag
        if element.attrib.has_key('visible'):
          node['visible'] = element.attrib['visible']
        created = {}
        created['version'] = element.attrib['version']
        created['changeset'] = element.attrib['changeset']
        created['timestamp'] = element.attrib['timestamp']
        if element.attrib.has_key('user'):
          created['user'] = element.attrib['user']
        if element.attrib.has_key('uid'):
          created['uid'] = element.attrib['uid']
        node['created'] = created
        if element.attrib.has_key('lat'):
          pos = []
          pos.append(float(element.attrib['lat']))
          pos.append(float(element.attrib['lon']))
          node['pos'] = pos
        address = {}
        for tag in element.iter("tag"):
        	if tag.attrib['k'] == 'name':
        		node['name'] = tag.attrib['v']
        	elif tag.attrib['k'] == 'sport':
        		node['sport'] = tag.attrib['v']
        	elif tag.attrib['k'] == 'amenity':
        		node['amenity'] = tag.attrib['v']
        	elif tag.attrib['k'] == 'addr:city':
        		address['city'] = filter_city_name(tag.attrib['v'])
        		count_city_name(address['city'])
        	elif tag.attrib['k'] == 'building':
        		address['building'] = tag.attrib['v']
        	elif tag.attrib['k'] == 'religion':
        		node['religion'] = tag.attrib['v']
        	elif re.match(housenumber,tag.attrib['k']):
        		address['housenumber'] = tag.attrib['v']
        	elif tag.attrib['k'] == 'addr:street':
        		street_suffix = filter_street_suffix(tag.attrib['v'])
        		address['street'] = filter_street_prefix(street_suffix)
        	elif tag.attrib['k'] == 'addr:postcode':
        		code = filter_postcode(tag.attrib['v'])
        		if code is not None:
        			address['postcode'] = code 

        if len(address) > 0:
          node['address'] = address
        node_refs = []
        for nd in element.iter("nd"):
          node_refs.append(nd.attrib['ref'])
        if len(node_refs) > 0:
          node['node_refs'] = node_refs

        return node
    else:
        return None

# This method will count city names in the city_list dictionary
def count_city_name(city_name):
	if city_list.has_key(city_name):
		city_list[city_name] += 1
	else:
		city_list[city_name] = 1

# This method will generate a dictionary with key as last word of street name
# and value as entire street name. It is useful to filter street names as per
# last word
def count_street_suffix(street):
	splitstreet = street.split(' ')
	lastword = splitstreet[-1]
	if streetcount_suffix.has_key(lastword):
		streetcount_suffix[lastword] += 1
	else:
		streetcount_suffix[lastword] = 1

# This method will generate a dictionary with key as first word of street name
# and value as entire street name. It is useful to filter street names as per
# first word
def count_street_prefix(street):
	splitstreet = street.split(' ')
	firstword = splitstreet[0]
	if streetcount_prefix.has_key(firstword):
		streetcount_prefix[firstword] += 1
	else:
		streetcount_prefix[firstword] = 1

# This method will filter city name. This will put many different styles of 
# city names under one umbrella. shape_element method will use this method
# before adding city name in JSON
def filter_city_name(city_name):
	san_jose = ['San Jose','san jose','San jose', 'san Jose',u'San Jos\xe9']
	campbell = ['Campbell','Campbelll','campbell']
	cupertino = ['Cupertino','cupertino']
	losgatos = ['Los Gato','Los Gatos','Los Gatos, CA']
	sunnyvale = ['Sunnyvale','SUnnyvale','Sunnyvale, CA','sunnyvale']
	santaclara = ['Santa Clara','Santa clara','santa Clara','santa clara']

	if city_name in san_jose:
		return 'San Jose'
	elif city_name in campbell:
		return 'Campbell'
	elif city_name in cupertino:
		return 'Cupertino'
	elif city_name in losgatos:
		return 'Los Gatos'
	elif city_name in sunnyvale:
		return 'Sunnyvale'
	elif city_name in santaclara:
		return 'Santa Clara'
	else:
		return city_name

# This method will filter street name suffixes. This will put many different styles of 
# suffixes like (Street, St, St., etc) under one umbrella. shape_element method will use this method
# before adding street value in JSON
def filter_street_suffix(street):
	splitstreet = street.split(' ')

	lastword = splitstreet[-1]
	boulevard = ['Boulevard','Boulvevard','Blvd']
	court = ['court','Court','Ct']
	road = ['Rd','Road','road']
	highway = ['Highway','Hwy']
	drive = ['Drive','Dr']
	st = ['Street','street','St']
	lane = ['Lane','Ln']
	square = ['Square','Sq']
	while not re.match(r'^[A-Za-z]',lastword):
		splitstreet.pop()
		lastword = splitstreet[-1]
		if lastword == 'PM':
			splitstreet.pop()
			lastword = splitstreet[-1]
	if re.match(r'^ave',lastword,re.IGNORECASE):
		splitstreet[-1] = "Avenue"
	elif re.match(r'cir',lastword,re.IGNORECASE):
		splitstreet[-1] = "Circle"
	elif lastword in boulevard:
		splitstreet[-1] = "Boulevard"
	elif lastword in court:
		splitstreet[-1] = "Court"
	elif lastword in road:
		splitstreet[-1] = "Road"
	elif lastword in highway:
		splitstreet[-1] = "Highway"
	elif lastword in drive:
		splitstreet[-1] = "Drive"
	elif lastword in st:
		splitstreet[-1] = "Street"
	elif lastword in lane:
		splitstreet[-1] = "Lane"
	elif lastword in square:
		splitstreet[-1] = "Square"
	
	new_street = ' '.join(splitstreet)
	count_street_suffix(new_street)
	return new_street

# This method will filter street name prefixes. This will put many different styles of 
# prefixes like (West, W, W., etc) under one umbrella. shape_element method will use this method
# before adding street value in JSON
def filter_street_prefix(street):
	splitstreet = street.split(' ')
	firstword = splitstreet[0]
	mount = ['Mount','Mt','Mt.']
	north = ['North', 'N','N.','north']
	south = ['South','S','S.','south']
	east = ['East','E','E.','east']
	west = ['West','W','W.','west']

	if firstword in mount:
		splitstreet[0] = 'Mount'
	elif firstword in north:
		splitstreet[0] = 'North'
	elif firstword in south:
		splitstreet[0] = 'South'
	elif firstword in east:
		splitstreet[0] = 'East'
	elif firstword in west:
		splitstreet[0] = 'West'

	new_street = ' '.join(splitstreet)
	count_street_prefix(new_street)
	return new_street

# This method will filter postal codes. It will bring the postal code is a uniform 5 digit format
def filter_postcode(postcode):
	pc = postcode.split(' ')
	if len(pc) == 2:
		return pc[1]
	pc = postcode.split('-')
	if len(pc) == 2:
		return pc[0]
	
	if len(postcode) > 5:
		code = postcode[:5]
		if re.match(r'^[0-9]*$',code):
			return code
		else:
			return None
	else:
		return postcode

# This method will obtain the generated JSON format from shape_element() method and dump to a
# JSON file. The filename of JSON file will be of format <XML File Name.xml>.json
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

# This method is not used in cleaning task. But this comes handy to find how many nodes, ways
# and relations are currently available in the dataset. This can be run from the main method
# directly.
def count_datapoints(filename):
	count_node = 0
	count_way = 0
	count_relation = 0
	tags = {}
	for _, element in ET.iterparse(filename):
		tag = element.tag
		if tag == 'node':
			count_node += 1
		elif tag == 'way':
			count_way += 1
		elif tag == 'relation':
			count_relation += 1
		elif tag == 'tag':
			for tag in element.iter('tag'):
				if tags.has_key(tag.attrib['k']):
					tags[tag.attrib['k']] += 1
				else:
					tags[tag.attrib['k']] = 1
	pprint.pprint(tags)
	
# Start of the code
if __name__ == "__main__":
	filename = "san-jose_california.osm"
	process_map(filename,True)