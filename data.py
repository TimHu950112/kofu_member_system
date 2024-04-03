from dotenv import load_dotenv
from datetime import datetime
import pymongo, certifi, requests, os, pytz

load_dotenv()

client = pymongo.MongoClient(
    "mongodb+srv://"
    + os.getenv("mongodb")
    + ".rpebx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=certifi.where(),
)
db = client.kofu_member_system


class User:
    def __init__(self, nickname, email, password):
        self.nickname = nickname
        self.email = email
        self.password = password

    def login(email, password):
        collection = db.members
        result = collection.find_one(
            {"$and": [{"email": email}, {"password": password}]}
        )
        if result == None:
            return False
        return result["nickname"]


class Member:
    def __init__(self, phone, name):
        self.phone = phone
        self.name = name

    def check(way, phone):
        # Search in new member
        collection = db.new
        result = collection.find_one({"phone": phone})
        # Search in old member
        collection = db.user
        result_1 = collection.find_one({"phone": phone})
        # Search in new_2024
        collection = db.new_2024
        result_2024 = collection.find_one({"phone": phone})

        # search_function
        if way == "search":
            # if result != None:
            #     return result["member_name"]
            if result_2024 != None:
                return result_2024["member_name"]
            return False

        # add_function
        if way == "add":
            # check if new member
            if result_2024 == None:
                # check if old member
                if result == None:
                    # check if old member
                    if result_1 == None:
                        return False
                    else:
                        return result_1["member_name"]
                else:
                    return result["member_name"]
            else:
                print("TRUE")
                return True

    def add(phone, member_name, forever):
        collection = db.new_2024
        collection.insert_one(
            {"member_name": member_name, "phone": phone, "forever": forever}
        )
        return True

    def predict_search(input_text):
        collection = db.new_2024
        matched_users = collection.find(
            {"phone": {"$regex": str(input_text), "$options": "i"}}
        )
        predictions = []
        for user in matched_users:
            predictions.append(user["phone"])  # 假設預測姓名
            if len(predictions) >= 3:
                break
        return predictions
    def count():
        collection = db.new_2024
        result = list(collection.find({}))
        return len(result)


class Order:
    def __init__(self, phone, number, items, date, status):
        self.phone = phone
        self.number = number
        self.items = items
        self.date = date
        self.status = status

    def order(phone, order_number, items, date, cost):
        print(items)
        collection = db.order
        collection.insert_one(
            {
                "phone": phone,
                "order-number": int(order_number),
                "原味肉粽(無蛋)": items[0][1],
                "原味肉粽(有蛋)": items[1][1],
                "干貝粽": items[2][1],
                "干貝鮑魚粽": items[3][1],
                "鹼粽": items[4][1],
                "紅豆鹼粽": items[5][1],
                "南部粽": items[6][1],
                "year": date[0],
                "month": date[1],
                "day": date[2],
                "time": date[3],
                "status": "0",
                "cost": cost,
            }
        )
        # Order.notify("\n編號"+order_number+"訂購成功")

    def search(order_number):
        collection = db.order
        result = collection.find_one({"order-number": int(order_number)})
        return result

    def change(phone, order_number, items, date, cost, user_data):
        Order.notify(
            "\n"
            + "【編號】"
            + str(order_number)
            + "\n【更改訂單備份】"
            + str(Order.search(order_number))
            + "\n【裝置資訊】"
            + user_data
        )
        collection = db.order
        collection.update_one(
            {"order-number": int(order_number)},
            {
                "$set": {
                    "phone": phone,
                    "原味肉粽(無蛋)": items[0][1],
                    "原味肉粽(有蛋)": items[1][1],
                    "干貝粽": items[2][1],
                    "干貝鮑魚粽": items[3][1],
                    "鹼粽": items[4][1],
                    "紅豆鹼粽": items[5][1],
                    "南部粽": items[6][1],
                    "year": date[0],
                    "month": date[1],
                    "day": date[2],
                    "time": date[3],
                    "status": "0",
                    "cost": cost,
                }
            },
        )

    def check(order_number):
        Order.notify("\n" + "【編號】" + str(order_number) + "\n【取貨通知】" + "取貨成功")
        collection = db.order
        collection.update_one(
            {"order-number": int(order_number)}, {"$set": {"status": "1"}}
        )

    def delete(order_number, user_data, delete_member):
        Order.notify(
            "\n"
            + "【編號】"
            + str(order_number)
            + "\n【刪除訂單備份】"
            + str(Order.search(order_number))
            + "\n【裝置資訊】"
            + user_data
            + "\n【刪除人員】"
            + delete_member
        )
        collection = db.order
        collection.delete_one({"order-number": int(order_number)})

    def notify(message):
        token = os.getenv("line_notify")
        # token="oIPzGSHqmO1r2yk7SjyxMfHJSzjoTk3WMedhRtbt2xB" 測試用token
        # HTTP 標頭參數與資料
        headers = {"Authorization": "Bearer " + token}
        data = {"message": message}

        # 以 requests 發送 POST 請求
        requests.post(
            "https://notify-api.line.me/api/notify", headers=headers, data=data
        )


class Coffee:
    def phone_check(input_text):
        collection = db.coffee
        matched_users = collection.find(
            {"phone": {"$regex": str(input_text), "$options": "i"}}
        )
        phone = []
        left = []
        for user in matched_users:
            phone.append(user["phone"])  # 假設預測姓名
            left.append([user["left"]["70"], user["left"]["80"]])
            if len(phone) >= 3:
                break
        return phone, left

    def add_coffee_function(phone, number, item):
        collection = db.coffee
        result = list(collection.find({"phone": phone}))
        print("result", result)
        if len(result) != 0:
            number_1 = result[0]["left"][item] + int(number)
            collection.update_one(
                {"phone": phone}, {"$set": {"left." + item: number_1}}
            )
            return "success"
        elif item == "70":
            collection.insert_one(
                {"phone": phone, "left": {"70": int(number), "80": 0}}
            )
            return "success"
        elif item == "80":
            collection.insert_one(
                {"phone": phone, "left": {"70": 0, "80": int(number)}}
            )
            return "success"

    def take_coffee_function(phone, number, item):
        collection = db.coffee
        result = list(collection.find({"phone": phone}))
        if len(result) != 0:
            number_1 = result[0]["left"][item] - int(number)
            collection.update_one(
                {"phone": phone}, {"$set": {"left." + item: number_1}}
            )
            return "取杯成功"
        else:
            return "查無此人"


class Money:
    def update_money_function(text, categories, amount):
        collection = db.money
        date = (
            datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d").split("-")
        )
        result = list(collection.find({}, {"_id": 1}).sort("_id", -1))
        if categories == "revenues":
            collection.insert_one(
                {
                    "_id": len(result) + 1,
                    "text": text,
                    "revenues": amount,
                    "expenditures": 0,
                    "year": date[0],
                    "month": date[1],
                }
            )
            return "上傳成功"
        elif categories == "expenditures":
            collection.insert_one(
                {
                    "_id": len(result) + 1,
                    "text": text,
                    "revenues": 0,
                    "expenditures": amount,
                    "year": date[0],
                    "month": date[1],
                }
            )
            return "上傳成功"
        else:
            return "上傳失敗"

    def check_money(year, month):
        collection = db.money
        date = (
            datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d").split("-")
        )
        print(date)
        if year == 0 or month == 0:
            return list(
                collection.find({"$and": [{"year": date[0]}, {"month": date[1]}]})
            )
        return list(collection.find({"$and": [{"year": year}, {"month": month}]}))

    def count_money(year, month):
        collection = db.money
        money = 0
        date = (
            datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d").split("-")
        )
        if year == 0 or month == 0:
            year = date[0]
            month = date[1]
        balance_list = []
        for i in list(collection.find({})):
            money += i["revenues"]
            money -= i["expenditures"]
            if i["year"] == year and i["month"] == month:
                balance_list.append(money)
        return money, balance_list

    def delete_money_function(id):
        collection = db.money
        collection.delete_one({"_id": int(id)})
        return "刪除成功"


class Line:
    def bind_phone(phone, line_id):
        collection = db.coffee
        if collection.find_one({"phone": phone}) == None:
            return "請先寄杯後再綁定手機"
        if (
            collection.find_one({"$and": [{"phone": phone}, {"line_id": line_id}]})
            != None
        ):
            return "您的手機已經綁定line"
        collection.update_one({"phone": phone}, {"$set": {"line_id": line_id}})
        return "手機" + phone + "綁定成功"

    def send_notify(phone):
        collection = db.coffee
        result = collection.find_one({"phone": phone})
        if result != None:
            try:
                return result["line_id"], result["left"]
            except:
                return False
        return False

    def check_coffee(line_id):
        collection = db.coffee
        result = collection.find_one({"line_id": line_id})
        if result != None:
            return result["left"]
        return False

    def save_data(message):
        token = os.getenv("coffee_data")
        headers = {"Authorization": "Bearer " + token}
        data = {"message": message}

        # 以 requests 發送 POST 請求
        requests.post(
            "https://notify-api.line.me/api/notify", headers=headers, data=data
        )
