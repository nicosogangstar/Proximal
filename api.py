#import everything mongoDB related
import pymongo
from pymongo import MongoClient, GEOSPHERE
from bson.objectid import ObjectId
from bson.son import SON
from gridfs import GridFS
from bson.json_util import dumps, loads

#make flask imports
from flask import Flask, request, session, render_template, make_response, redirect, url_for, jsonify

import bcrypt

#do flask shit
app = Flask(__name__)

#import the db and posts collection
client = MongoClient()
db = client.proximal
posts = db.posts
images = db.images
users = db.users

grid = GridFS(db, collection='images')


@app.route('/getsession', methods=['GET'])
def getsession():
	if "user" not in session:
		return "Not logged in"
	else:
		user = loads(session["user"])
		return "Welcome " + user["username"]

#posting stuff
@app.route('/post', methods=['POST'])
def makepost():
	#ensure it is a valid request and retrieve all of the values
	if request.method == 'POST':
		post_data = request.get_json()
		longitude = post_data['longitude']
		latitude = post_data['latitude']
		caption = post_data['caption']
		image = post_data['image']
	else:
		return "POST protocol required.\n"
	#insert value to db
	image_id = grid.put(image, encoding='utf-8')
	posts.insert({'loc': {'type': 'Point', 'coordinates': [longitude, latitude]}, 'image_id': image_id, 'caption': caption})
	return "Complete.\n"

#viewing stuff
@app.route('/view', methods=['GET'])
def getposts():
	#ensure it is a valid request and retrieve all of the values
	if request.method == 'GET':
		longitude = float(request.args.get("longitude"))
		latitude = float(request.args.get("latitude"))
		radius = float(request.args.get("radius"))
		page = int(request.args.get("page"))
		numpost = int(request.args.get("numpost"))
		if numpost < 0 or numpost > 25:
			return "Query count too high or low.\n"
	else:
		return "GET protocol required.\n"

	docs = []
	for doc in posts.find({"loc":{"$near":{"$geometry":{"type":"Point","coordinates":[longitude,latitude]},"$maxDistance":radius}}}).skip(page*numpost).limit(numpost).sort("_id", -1):
		image_id = doc["image_id"]
		image_data = grid.get(image_id).read()
		doc["image_data"] = image_data.decode("utf-8")
		del doc["image_id"]
		docs.append(doc)
	return "{\"posts\":"+dumps(docs)+"}"

#vote on a post
@app.route('/vote', methods=['GET', 'POST'])
def vote():
	#ensure it is a valid request and retrieve all of the values
	if request.method == 'GET':
		post_id = float(request.args.get("post_id"))
		vote = float(request.args.get("vote"))
	else:
		return "GET protocol required.\n"

	if vote > 0:
		posts.update({"_id": ObjectId(post_id)}, {"$inc": {"upvotes" : vote}})
	elif vote < 0:
		posts.update({"_id": ObjectId(post_id)}, {"$inc": {"downvotes" : vote}})
	else:
		return "Vote value cannot be zero.\n"
	return "Success.\n"

#register function
@app.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'POST':
		username = request.form["username"]
		if users.find_one({"username": username}) is None:
			hashed_password = bcrypt.hashpw(request.form["password"], bcrypt.gensalt())
			users.insert({"username": username, "hashed_password": hashed_password})
			return "Success\n"
		elif str(users.find_one({"username": username})['username'])==username:
			return "Duplicate user..\n"
	else:
		return render_template("register.html")

#login function
@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		username = request.form["username"]
		password = request.form["password"]
		hashed_password = str(users.find_one({"username": username})['hashed_password'])
		if bcrypt.hashpw(password, hashed_password) == hashed_password:
			session["user"] = dumps(users.find_one({"username": username}))
			return "Login information correct!\n"

		return "Login information incorrect.\n"

	else:
		return render_template("login.html")

@app.route('/logout')
def logout():
	# remove the username from the session if it's there
	session.pop('user', None)
	return "Logged out.\n"

#homepage
@app.route('/')
def home():
	return render_template('index.html')

@app.route('/test')
def test():
	return render_template('testJS.html')

# set the secret key. ZUPPPA S3CR37ZZZZZ
app.secret_key = '\xd9\x18\xf2\x1bJK\x85\xa0q\xe6?s]\xe2(\xae:\xe9\xef\x08\xb2\xee\xbb\xb4'

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=80)