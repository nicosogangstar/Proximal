import pymongo
from pymongo import MongoClient, GEOSPHERE

#drop db
client = MongoClient()
client.drop_database('proximal')

#setup deb for new data
db = client.proximal
db.posts.create_index([("loc", GEOSPHERE)])