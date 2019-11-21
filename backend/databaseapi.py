import pymongo
from pymongo import MongoClient

def userSequenceByUidPid(userid, problemid):
    client = MongoClient("127.0.0.1", 27017)
    db = client.trumptech
    collection = db.records
    cursor = collection.find({"userid":userid, "d_source":problemid}, {"_id":0,"pageX":1,"pageY":1,"type":1})
    return list(cursor)

def problemSequenceById(problemid):
    client = MongoClient("127.0.0.1", 27017)
    db = client.trumptech
    collection = db.records
    cursor = collection.find({"d_source":problemid}, {"_id":0,"pageX":1,"pageY":1,"userid":1})
    return list(cursor)

def userSequenceByProblem(problemid):
    client = MongoClient("127.0.0.1", 27017)
    db = client.trumptech
    collection = db.records
    cursor = list(collection.aggregate(
            [
            {"$match": {"d_source": problemid}},
            {"$group": {
                    "_id":"$userid",
                    "data":{
                        "$push":{
                            "time":"$dt_timestamp",
                            "time2": "$timeStamp",
                            "x":"$pageX",
                            "y":"$pageY",
                            "type":"$type"
                        }
                    },
                }
            },
            { "$sort": { "data.time": -1, "data.time2": -1 } },
            ]))
    return cursor

def userSequenceByProblemByEventTime(problemid):
    client = MongoClient("127.0.0.1", 27017)
    db = client.trumptech
    collection = db.records
    cursor = list(collection.aggregate(
            [
            {"$match": {"d_source": problemid}},
            {"$group": {
                    "_id":"$userid",
                    "data":{
                        "$push":{
                            "timestamp":"$timeStamp",
                            "pageX":"$pageX",
                            "pageY":"$pageY",
                            "type":"$type"
                        }
                    },
                }
            },
            { "$sort": { "data.timestamp": -1 } },
            ]))
    return cursor
