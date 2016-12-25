# File : pymongo_impl.py
# Date : 12/24/2016
# Owner : Rahul Daware
# Description : This file contains data querying tasks. This code is a part of 
#				Data Wrangling with MongoDB project.

from pymongo import MongoClient
import pprint

client = MongoClient('mongodb://localhost:27017/')

db = client.san_jose

document_count = db.osm.find().count()
print 'Number of Documents : ', document_count

nodes_count = db.osm.find({"type":"node"}).count()
print 'Number of Nodes : ', nodes_count

ways_count = db.osm.find({"type":"way"}).count()
print 'Number of Ways : ',ways_count

top_5_created_user = db.osm.aggregate([{"$group" : {"_id" : "$created.user", "count" : {"$sum" : 1}}},
				 {"$sort" : {"count" : -1}}, {"$limit" : 5}])
pprint.pprint(list(top_5_created_user))

top_5_cities = db.osm.aggregate([{"$group" : {"_id" : "$address.city", "count" : {"$sum" : 1}}},
				 {"$sort" : {"count" : -1}}, {"$limit" : 5}])
pprint.pprint(list(top_5_cities))

top_5_religion = db.osm.aggregate([{"$match":{"religion":{"$exists":1}}},{"$group" : {"_id" : "$religion", "count" : {"$sum" : 1}}},
				 {"$sort" : {"count" : -1}}, {"$limit" : 5}])
pprint.pprint(list(top_5_religion))

top_5_amenities = db.osm.aggregate([{"$match":{"amenity":{"$exists":1}}},{"$group" : {"_id" : "$amenity", "count" : {"$sum" : 1}}},
				 {"$sort" : {"count" : -1}}, {"$limit" : 5}])
pprint.pprint(list(top_5_amenities))

top_5_sport = db.osm.aggregate([{"$match":{"sport":{"$exists":1}}},{"$group" : {"_id" : "$sport", "count" : {"$sum" : 1}}},
				 {"$sort" : {"count" : -1}}, {"$limit" : 5}])
pprint.pprint(list(top_5_sport))