import pymongo

from typing import Dict

conn = pymongo.MongoClient("mongodb://localhost:27017/")

db = conn["stalk-market"]

collection = db["users"]


def get_user_by_id(id: int):
    return collection.find_one({"_id": id})


def get_user_by_username(username: str, server_id: int):
    return collection.find_one({"username": username, "servers": server_id})


def get_users(query, projection):
    return list(collection.find(query, projection))


def upsert_user_data(id: int, set: Dict, addToSet: Dict):
    return (
        collection.update_one(
            {"_id": id}, {"$set": set, "$addToSet": addToSet}, upsert=True
        )
    ).acknowledged


def rename_users_data(data: Dict):
    return (collection.update_many({}, {"$rename": data})).acknowledged


def remove_user_data(id: int, data):
    return (collection.update_one({"_id": id}, {"$unset": data})).acknowledged


def remove_users_data(data):
    return (collection.update_many({}, {"$unset": data})).acknowledged


conn.close()
