
import pymongo

from datetime import datetime

conn = pymongo.MongoClient("mongodb://localhost:27017/")

db = conn["stalk-market"]

collection = db["users"]

def get_user(id: int):
  return collection.find_one({'_id': id})

def get_users():
  return list(collection.find())

def upsert_user_data(id: int, data): 
  return (collection.update_one({'_id': id}, {"$set": data}, upsert=True)).acknowledged

def remove_user_data(id: int, data):
  return (collection.update_one({'_id': id}, {"$unset": data})).acknowledged

def remove_all_data(data):
  return (collection.update_many({}, {'$unset': data})).acknowledged

conn.close()
