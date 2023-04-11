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

   
collection=db.order
collection.insert_one({'phone': '0937184033', 'order-number': 122, '原味肉粽(無蛋)': 5, '原味肉粽(有蛋)': 0, '干貝粽': 0, '干貝鮑魚粽': 0, '鹼粽': 0, '紅豆鹼粽': 5, '南部粽': 0, 'year': '2023', 'month': '06', 'day': '20', 'time': '12:50', 'status': '0', 'cost': 625})

    