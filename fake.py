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

for i in range(10):
    collection=db.order
    collection.insert_one({
    "phone":str(random.randrange(10)*10),
    "order-number":"00"+str(random.randrange(10)),
    "原味肉粽(無蛋)":str(random.randrange(10)),
    "原味肉粽(有蛋)":str(random.randrange(10)),
    "干貝粽":str(random.randrange(10)),
    "干貝鮑魚粽":str(random.randrange(10)),
    "鹼粽":str(random.randrange(10)),
    "紅豆鹼粽":str(random.randrange(10)),
    "南部粽":str(random.randrange(10)),
    "year":"2022",
    "month":"02",
    "day":"02",
    "time":"20:15",
    "status":"not"
    })
    print(i)