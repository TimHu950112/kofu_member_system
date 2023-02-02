from crypt import methods
from imp import reload
from flask import*
from unittest import result
import pymongo
import certifi
from requests import Session
import random
import string
import time
#初始化資料庫連線
client=pymongo.MongoClient("mongodb+srv://root:root123@cluster0.rpebx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=certifi.where())
db=client.kofu_member_system
print("\n"+"資料庫連線成功".center(87,"*")+"\n")


collection=db.order
result=list(collection.find({"month":"02"}))
print(result)
cost=0
for i in result:
    cost+=i["原味肉粽(無蛋)"]
print(cost)