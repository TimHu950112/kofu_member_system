from crypt import methods
from imp import reload
from flask import*
from crypt import methods
from imp import reload
from flask import*
from unittest import result
import pymongo
import certifi
from requests import Session
import random

#導入物件設定
from data import*

#初始化資料庫連線
client=pymongo.MongoClient("mongodb+srv://root:root123@cluster0.rpebx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=certifi.where())
db=client.kofu_member_system
print("\n"+"資料庫連線成功".center(87,"*")+"\n")

for i in range(2000):   
    collection=db.order
    collection.insert_one({
    "phone":"0979928770",
    "order-number":i+1105,
    "原味肉粽(無蛋)":str(random.randrange(1000)),
    "原味肉粽(有蛋)":str(random.randrange(1000)),
    "干貝粽":str(random.randrange(1000)),
    "干貝鮑魚粽":str(random.randrange(1000)),
    "鹼粽":str(random.randrange(1000)),
    "紅豆鹼粽":str(random.randrange(1000)),
    "南部粽":str(random.randrange(1000)),
    "year":"2023",
    "month":"02",
    "day":"28",
    "time":"8:10",
    "status":"0",
    "cost":str(random.randrange(100000000))
    })
    print(i)
    