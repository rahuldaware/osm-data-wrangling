
# Open Street Map Data Wrangling with Python and MongoDB

This project is a wok of Data Wrangling over a dataset downloaded from OpenStreetMaps website of city of San Jose. After importing the XML data into Python code, we will analyse, clean, convert to JSON and then import data into a mongoDB dataset. After importing data into a Mongo DB database, we will perform some queries and gain additional knowledge from the dataset.

## Relevant Files
1. ```README.md``` : Contains the entire project report for Github purpose.  
2. ```wrangling.py``` : Contains all methods with all wrangling tasks. All the functions are described properly in the source code.  
3. ```pymongo_impl.py``` : Contains all queries run against the Mongo DB database.  
4. ```report.html``` : HTML format of this report
5. ```report.ipynb``` : iPython format of the report
6. ```sample.osm``` : A sample file which is first 10 MB of San Jose OSM database  

 
Note:  The dataset is not provided in this project repository. To download, please find the link below. After running wrangling tasks on the dataset, A JSON file will be generated. It should be imported into your Mongo DB dataset with database name as "san_jose" and collection name as "osm".

    

## Code Implementation

### Step 1 : Downloading and Importing Dataset into Python

The San Jose city database is downloaded from following link : [San Jose Dataset](https://mapzen.com/data/metro-extracts/metro/san-jose_california/). All the python code implementation is available in "wrangling.py" file

### Step 2: Problems faced in the Dataset

   This dataset has 793 different types of tags. It is out of scope to clean each of them. For the purpose of this project, I will clean attributes related to address information in this project. Let us discuss some of the problems encountered in these address values.
   
   The housenumber parameter has many aliases like addr:housenumber_1, addr:housenumber_2, etc. It is important to bring all of them to one standard (housenumber). For this, I will use regular expression to match all types of housenumber keys and save them under one key in JSON format.

   In wrangling.py, you can find many methods written to print the dataset to provide more information. For example, ```count_postcode()``` will count the number of different types of postal codes. I found that many postal codes were node in common 5 digit format. I found irregular format like : '95014-7412' or 'CA 94035'. Before adding postal code to JSON, they have to pass through a filtering method called ```filter_postcode()```.
   
   There is no uniformity observed in the naming of streets. Let us start with suffixes. For example, A street may end with "Street",'street' or 'St'. Similar case has been observed with others like Avenue and Bolevard. We can bring al such similar suffixes under one umbrella. The function ```filter_street_suffix()``` will perform this task before adding street name to JSON.
   
   The ```count_city_name()``` function counts the number of nodes in each city name. After running this function, I found out that there is spanish version of city name 'San Josè'. Also there are case sensitive versions. It is important to get all of them under one name. Hence, the ```filter_city_name()``` function will do this task. The city names count now got reduced to just 16.

### Step 3 : Importing JSON into MongoDB dataset

After cleaning a good number of areas, lets move on to import the generated JSON into the Mongo DB dataset. We have generated a JSON file of 383 MB from an XML file of 273 MB. To import use the following command : ```mongoimport -d san_jose -c osm --file san-jose_california.osm.json```

### Step 4 : Running basic queries on MongoDB dataset

  The following queries are run together in a python file (```pymongo_impl.py```). To obtain these results, please import the JSON and run the pymongo implementation python code.  
  
  1. Number of Documents  
     Command : ```db.osm.find().count()```  
     Ans : 1464135  
    
  2. Number of Nodes  
    Command : ```db.osm.find({"type":"node"}).count()```  
    Ans : 1292173  
    
  3. Number of Ways  
     Command : ```db.osm.find({"type":"way"}).count()```  
     Ans : 171962  
    
  4. Top 5 contributor to this dataset  
     Command : ```db.osm.aggregate([{"$group" : {"_id" : "$created.user", "count" : {"$sum" : 1}}},{"$sort" : {"count" : -1}}, {"$limit" : 5}])```  
    Ans : [{u'_id': u'nmixter', u'count': 288566},  
 {u'_id': u'mk408', u'count': 152025},  
 {u'_id': u'Bike Mapper', u'count': 81998},  
 {u'_id': u'samely', u'count': 77744},  
 {u'_id': u'dannykath', u'count': 71938}]  
 
  5. Top 5 cities in the dataset  
     Command : ```db.osm.aggregate([{"$group" : {"_id" : "$address.city", "count" : {"$sum" : 1}}},{"$sort" : {"count" : -1}}, {"$limit" : 5}])```  
     Ans : [{u'_id': None, u'count': 1458677},  
 {u'_id': u'Sunnyvale', u'count': 3403},  
 {u'_id': u'San Jose', u'count': 860},  
 {u'_id': u'Morgan Hill', u'count': 373},  
 {u'_id': u'Santa Clara', u'count': 311}]   
 
 
#### Comments on the above results :
 
 
   1.  There are higher number of nodes as compared to ways in this dataset.  
   2.  About 19% of the dataset is contributed by the top contributor.  
   3.  About 46% of the dataset is contributed by the op 5 contributors.  
   4.  After running aggregation query on the cities, we find lot of nodes are without cities. About 99% of places do not have city information.
                 

### Step 5: Running additional queries on the dataset

The following queries are also a part of ```pymongo_impl.py``` file. Now Let us find some more information from this dataset. There are many more tags available. I have run a few of them below :    

1. Which are the top 5 religions in San Jose City?  
    Command : ```db.osm.aggregate([{"$match":{"religion":{"$exists":1}}},{"$group" : {"_id" : "$religion", "count" : {"$sum" : 1}}},{"$sort" : {"count" : -1}}, {"$limit" : 5}])```  
    Ans : [{u'_id': u'christian', u'count': 333},  
              {u'_id': u'jewish', u'count': 5},  
              {u'_id': u'buddhist', u'count': 5},  
              {u'_id': u'muslim', u'count': 3},  
              {u'_id': u'unitarian_universalist', u'count': 2}]  
 
2. Which are top 5 amenities in this dataset?  
    Command : ```db.osm.aggregate([{"$match":{"amenity":{"$exists":1}}},{"$group" : {"_id" : "$amenity", "count" : {"$sum" : 1}}},{"$sort" : {"count" : -1}}, {"$limit" : 5}])```  
    Ans: [{u'_id': u'parking', u'count': 1848},  
 {u'_id': u'restaurant', u'count': 937},    
 {u'_id': u'school', u'count': 532},  
 {u'_id': u'fast_food', u'count': 477},  
 {u'_id': u'place_of_worship', u'count': 343}]  
3. Which is the most popular sport in San Jose City?   
    Command : ```db.osm.aggregate([{"$match":{"sport":{"$exists":1}}},{"$group" : {"_id" : "$sport", "count" : {"$sum" : 1}}},
{"$sort" : {"count" : -1}}, {"$limit" : 5}]) ```  
  Ans:[{u'_id': u'tennis', u'count': 379},  
 {u'_id': u'basketball', u'count': 309},  
 {u'_id': u'baseball', u'count': 238},  
 {u'_id': u'swimming', u'count': 96},  
 {u'_id': u'soccer', u'count': 79}]  



### Step 6 : Conclusion

 The San Jose City OSM dataset contains 793 different types of tags. Hence, you can see, it is very difficult to find uniform data easy enough to be used directly with Mongo DB. Hence, I tried to clean the data as much as possible. We can add more attributes to nodes and run more queries on it. I found a lot of missing data. For example, I tried to run a query to find which is most popular cuisine in San Jose. I found there is no restaurant type information available. Some queries did go through successfully. For example, I was able to find that tennis is the most popular sport in San Jose as there are higher number of nodes with tennis sport facility.
