from dotenv import load_dotenv
import pymongo,certifi,requests,os

load_dotenv()

client=pymongo.MongoClient("mongodb+srv://"+os.getenv("mongodb")+".rpebx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=certifi.where())
db=client.kofu_member_system

class User:
    def __init__(self,nickname,email,password):
        self.nickname=nickname
        self.email=email
        self.password=password

    def login(email,password):
        collection=db.members
        result=collection.find_one({
            "$and":[
                {"email":email},
                {"password":password}
            ]
        })
        if result==None:
            return False
        return result["nickname"]

class Member:
    def __init__(self,phone,name):
        self.phone=phone
        self.name=name
    def check(way,phone):
        #Search in new member
        collection=db.new
        result=collection.find_one({"phone":phone})
        #Search in old member
        collection=db.user
        result_1=collection.find_one({"phone":phone})

        #search_function
        if way=="search":
            #old member
            # if result_1!=None:
            #     return result_1["member_name"]
            #new member
            if result!=None:
                return result["member_name"]
            return False

        #add_function
        if way=="add":
            #check if new member
            if result==None:
                #check if old member
                if result_1==None:
                    print("re1")
                    return None
                else:
                    print("re2")
                    return result_1["member_name"]
            else:
                print("TRUE")
                return True
    def add(phone,member_name,forever):
        collection=db.new
        collection.insert_one({
        "member_name":member_name,
        "phone":phone,
        "forever":forever})
        return True 
class Order:
    def __init__(self,phone,number,items,date,status):
        self.phone=phone
        self.number=number
        self.items=items
        self.date=date
        self.status=status

    def order(phone,order_number,items,date,cost):
        print(items)
        collection=db.order
        collection.insert_one({
        "phone":phone,
        "order-number":int(order_number),
        "原味肉粽(無蛋)":items[0][1],
        "原味肉粽(有蛋)":items[1][1],
        "干貝粽":items[2][1],
        "干貝鮑魚粽":items[3][1],
        "鹼粽":items[4][1],
        "紅豆鹼粽":items[5][1],
        "南部粽":items[6][1],
        "year":date[0],
        "month":date[1],
        "day":date[2],
        "time":date[3],
        "status":"0",
        "cost":cost
        })
        # Order.notify("\n編號"+order_number+"訂購成功")
    def search(order_number):
        collection=db.order
        result=collection.find_one({"order-number":int(order_number)})
        return result
    def change(phone,order_number,items,date,cost,user_data):
        Order.notify("\n"+ "【編號】"+str(order_number)+"\n【更改訂單備份】"+str(Order.search(order_number))+"\n【裝置資訊】"+user_data)
        collection=db.order
        collection.update_one({
        "order-number":int(order_number)},
        {"$set":{
        "phone":phone,
        "原味肉粽(無蛋)":items[0][1],
        "原味肉粽(有蛋)":items[1][1],
        "干貝粽":items[2][1],
        "干貝鮑魚粽":items[3][1],
        "鹼粽":items[4][1],
        "紅豆鹼粽":items[5][1],
        "南部粽":items[6][1],
        "year":date[0],
        "month":date[1],
        "day":date[2],
        "time":date[3],
        "status":"0",
        "cost":cost
        }
        })
    def check(order_number):
        Order.notify("\n"+ "【編號】"+str(order_number)+"\n【取貨通知】"+"取貨成功")
        collection=db.order
        collection.update_one({
        "order-number":int(order_number)},
        {"$set":{
        "status":"1"
        }
        })
    def delete(order_number,user_data,delete_member):
        Order.notify("\n"+ "【編號】"+str(order_number)+"\n【刪除訂單備份】"+str(Order.search(order_number))+"\n【裝置資訊】"+user_data+"\n【刪除人員】"+delete_member)
        collection=db.order
        collection.delete_one({
        "order-number":int(order_number)})
    def notify(message):
        token = os.getenv("line_notify")
        # token="oIPzGSHqmO1r2yk7SjyxMfHJSzjoTk3WMedhRtbt2xB" 測試用token
        # HTTP 標頭參數與資料
        headers = { "Authorization": "Bearer " + token }
        data = { 'message': message }

        # 以 requests 發送 POST 請求
        requests.post("https://notify-api.line.me/api/notify",
            headers = headers, data = data)