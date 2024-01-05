from __future__ import unicode_literals
from flask import *
from datetime import datetime, timedelta
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from multiprocessing import Process
import pymongo, certifi, pytz, re, os

load_dotenv()

# 導入物件設定
from data import *

# 初始化資料庫連線
client = pymongo.MongoClient(
    "mongodb+srv://"
    + os.getenv("mongodb")
    + ".rpebx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=certifi.where(),
)
db = client.kofu_member_system
print("\n" + "\x1b[6;30;42m" + "資料庫連線成功".center(87) + "\x1b[0m" + "\n")

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi(os.getenv("line_access"))
handler = WebhookHandler(os.getenv("line_secret"))

# 初始化 flask 伺服器
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.getenv("secret_key")


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)  # 設定 session 的有效期限


# index_page
@app.route("/")
def index():
    if "member_data" in session:
        if session["member_data"]["nickname"] == "Yuan":
            if request.args.get("year") == None or request.args.get("month") == None:
                return render_template(
                    "money.html",
                    data=Money.check_money(0, 0),
                    balance=Money.count_money(0, 0)[0],
                    balance_list=Money.count_money(0, 0)[1],
                )
            else:
                return render_template(
                    "money.html",
                    data=Money.check_money(
                        request.args.get("year"), request.args.get("month")
                    ),
                    balance=Money.count_money(
                        request.args.get("year"), request.args.get("month")
                    )[0],
                    balance_list=Money.count_money(
                        request.args.get("year"), request.args.get("month")
                    )[1],
                )
        return redirect("/function")
    return render_template("login.html")


# error_page
@app.route("/error")
def error():
    message = request.args.get("msg", "發生錯誤，請聯繫客服")
    return render_template("error.html", message=message)


# add_member_page
@app.route("/add_page")
def add_page():
    if "member_data" in session:
        nickname = session["member_data"]["nickname"]
        member_num=Member.count()
        return render_template("check_old.html", nickname=nickname, member_num=member_num)
    flash("請先登入")
    return redirect("/")


# function_page
@app.route("/function")
def function():
    if "member_data" in session:
        return render_template("function.html")
    flash("請先登入")
    return redirect("/")


# search_order_page
@app.route("/order_page")
def order_page():
    if "member_data" in session:
        nickname = session["member_data"]["nickname"]
        # 判斷有無今日訂單
        collection = db.order
        date = (
            datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d").split("-")
        )
        result = list(
            collection.find(
                {
                    "$and": [
                        {"year": date[0]},
                        {"month": date[1]},
                        {"day": date[2]},
                        {"status": "0"},
                    ]
                }
            )
        )
        if not result:
            order_notify = None
        else:
            order_notify = len(result)
        return render_template(
            "order_page.html", nickname=nickname, order_notify=order_notify
        )
    flash("請先登入")
    return redirect("/")


# add_order_page
@app.route("/add_order_page")
def add_order_page():
    if "member_data" in session:
        session["edit"] = "none"
        session["price"] = [
            ["原味肉粽（無蛋）", 85, "o_n_price"],
            ["原味肉粽（有蛋）", 95, "o_price"],
            ["干貝粽", 158, "sc_price"],
            ["干貝鮑魚粽", 188, "sc_a_price"],
            ["鹼粽", 35, "a_price"],
            ["紅豆鹼粽", 40, "b_a_price"],
            ["南部粽", 85, "so_price"],
        ]
        session["items"] = [
            ["原味肉粽（無蛋）", 0, "o_n_item"],
            ["原味肉粽（有蛋）", 0, "o_item"],
            ["干貝粽", 0, "sc_item"],
            ["干貝鮑魚粽", 0, "sc_a_item"],
            ["鹼粽", 0, "a_item"],
            ["紅豆鹼粽", 0, "b_a_item"],
            ["南部粽", 0, "so_item"],
        ]
        session["each_cost"] = [
            ["原味肉粽（無蛋）", 0, "o_n_cost"],
            ["原味肉粽（有蛋）", 0, "o_cost"],
            ["干貝粽", 0, "sc_cost"],
            ["干貝鮑魚粽", 0, "sc_a_cost"],
            ["鹼粽", 0, "a_cost"],
            ["紅豆鹼粽", 0, "b_a_cost"],
            ["南部粽", 0, "so_cost"],
        ]
        collection = db.order
        result1 = list(
            collection.find({}, {"order-number": 1}).sort("order-number", -1)
        )
        # 單日訂單上限
        date = (
            datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d").split("-")
        )
        result = list(
            collection.find(
                {"$and": [{"year": date[0]}, {"month": date[1]}, {"day": date[2]}]}
            )
        )
        if len(result) > 100:
            flash("已達當日訂單上限（100張）！")
        session["order-number"] = str(int(result1[0]["order-number"]) + 1)
        return render_template(
            "add_order_page.html",
            price=session["price"],
            items=session["items"],
            cost=0,
            order_number=session["order-number"],
            each_cost=session["each_cost"],
        )
    flash("請先登入")
    return redirect("/")


# login_function
@app.route("/login", methods=["GET", "POST"])
def login():
    result = User.login(request.form["email"], request.form["password"])
    if result == False:
        Order.notify("\n" + "【帳號密碼輸入錯誤】")
        return redirect("/error?msg=帳號或密碼錯誤")
    session["member_data"] = {
        "email": request.form["email"],
        "password": request.form["password"],
        "nickname": result,
    }
    return redirect("/")


# logout_funtion
@app.route("/logout")
def logout():
    session.clear()
    flash("登出成功")
    return redirect("/")


# check_add_member_function
# To check if he is old member or already a new member
@app.route("/check_old", methods=["GET", "POST"])
def check_old():
    if "member_data" in session:
        session["phone"] = request.form["phone"]
        print("session_log:")
        print(session["phone"])
        member_status = Member.check("add", session["phone"])
        print(member_status)
        if member_status == True:
            print('已經是新會員')
            flash("已經是新會員")
            return render_template("check_old.html")
        if member_status == False:
            return render_template(
                "add_new.html", phone=session["phone"], member_name=""
            )
        flash("舊會員" + member_status + "請確認是否註冊為永久會員")
        return render_template(
            "add_new.html", phone=session["phone"], member_name=member_status
        )
    flash("請先登入")
    return redirect("/")


# add_member_function
# To add member to mongodb
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.form.get("forever") == "forever":
        forever = "forever"
    else:
        forever = "not"
    Member.add(request.form["phone"], request.form["member_name"], forever)
    flash("會員註冊成功")
    return render_template("check_old.html")


# search_member_function
@app.route("/search", methods=["GET", "POST"])
def search():
    if "member_data" in session:
        status = Member.check("search", request.form["phone"])
        if status == False:
            flash("查無資料")
            return render_template("function.html", status="無資料")
        return render_template("function.html", status=status)
    flash("請先登入")
    return redirect("/")


@app.route("/quick_search", methods=["GET", "POST"])
def quick_search():
    if "member_data" in session:
        status = Member.check("search", request.args.get("phone"))
        if status == False:
            flash("查無資料")
            return render_template("function.html", status="無資料")
        return render_template("function.html", status=status)
    flash("請先登入")
    return redirect("/")


# search_order_function
@app.route("/search_order", methods=["GET", "POST"])
def search_order():
    collection = db.order
    if request.form["item"] == "請選取搜尋方式":
        flash("請選擇搜尋方式")
        return redirect("/order_page")
    if request.form["item"] != "number":
        if request.form["item"] != "today":
            if request.form["item"] != "not_receive":
                if not request.form["phone"]:
                    flash("搜尋欄不能為空白")
                    return redirect("/order_page")
    if request.form["item"] == "order-number":
        result = list(collection.find({"order-number": int(request.form["phone"])}))
        not_recieve = len(result) - len(
            list(
                collection.find(
                    {
                        "$and": [
                            {"order-number": int(request.form["phone"])},
                            {"status": "1"},
                        ]
                    }
                )
            )
        )
    if request.form["item"] == "phone":
        result = list(
            collection.find({"phone": {"$regex": request.form["phone"]}}).sort(
                [("status", 1), ("year", 1), ["month", 1], ["day", 1]]
            )
        )
        not_recieve = len(result) - len(
            list(
                collection.find(
                    {"$and": [{"phone": request.form["phone"]}, {"status": "1"}]}
                )
            )
        )
    if request.form["item"] == "date":
        date = request.form["phone"].split("-")
        result = list(
            collection.find(
                {"$and": [{"year": date[0]}, {"month": date[1]}, {"day": date[2]}]}
            ).sort([("status", 1), ("year", 1), ["month", 1], ["day", 1]])
        )
        not_recieve = len(result) - len(
            list(
                collection.find(
                    {
                        "$and": [
                            {"year": date[0]},
                            {"month": date[1]},
                            {"day": date[2]},
                            {"status": "1"},
                        ]
                    }
                )
            )
        )
    if request.form["item"] == "today":
        date = (
            datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d").split("-")
        )
        result = list(
            collection.find(
                {"$and": [{"year": date[0]}, {"month": date[1]}, {"day": date[2]}]}
            ).sort([("status", 1), ("year", 1), ["month", 1], ["day", 1]])
        )
        not_recieve = len(result) - len(
            list(
                collection.find(
                    {
                        "$and": [
                            {"year": date[0]},
                            {"month": date[1]},
                            {"day": date[2]},
                            {"status": "1"},
                        ]
                    }
                )
            )
        )
    if request.form["item"] == "not_receive":
        result = list(
            collection.find({"status": "0"}).sort(
                [("status", 1), ("year", 1), ["month", 1], ["day", 1]]
            )
        )
        not_recieve = len(result)
    if request.form["item"] == "number":
        if (
            session["member_data"]["nickname"] == "TimHu"
            or session["member_data"]["nickname"] == "Yuan"
            or session["member_data"]["nickname"] == "雪婷"
        ):
            order_object = []
            result = list(
                collection.find().sort(
                    [("status", 1), ("year", 1), ["month", 1], ["day", 1]]
                )
            )
            # result.find({})
        else:
            flash("你沒有權限查看此內容")
            return redirect("/order_page")
        not_recieve = len(result) - len(list(collection.find({"status": "1"})))
    order_object = []
    for i in range(len(result)):
        order_object.append(
            Order(
                result[i]["phone"],
                result[i]["order-number"],
                {
                    "原味肉粽(無蛋)": result[i]["原味肉粽(無蛋)"],
                    "原味肉粽(有蛋)": result[i]["原味肉粽(有蛋)"],
                    "干貝粽": result[i]["干貝粽"],
                    "干貝鮑魚粽": result[i]["干貝鮑魚粽"],
                    "鹼粽": result[i]["鹼粽"],
                    "紅豆鹼粽": result[i]["紅豆鹼粽"],
                    "南部粽": result[i]["南部粽"],
                },
                result[i]["year"]
                + "-"
                + result[i]["month"]
                + "-"
                + result[i]["day"]
                + " "
                + result[i]["time"],
                result[i]["status"],
            )
        )
        number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(len(order_object)):
        number_list[0] += int(order_object[i].items["原味肉粽(無蛋)"])
        number_list[1] += int(order_object[i].items["原味肉粽(有蛋)"])
        number_list[2] += int(order_object[i].items["干貝粽"])
        number_list[3] += int(order_object[i].items["干貝鮑魚粽"])
        number_list[4] += int(order_object[i].items["鹼粽"])
        number_list[5] += int(order_object[i].items["紅豆鹼粽"])
        number_list[6] += int(order_object[i].items["南部粽"])
        number_list[7] += 1

    try:
        print(number_list)
        number_list[8] = not_recieve
    except:
        number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    # print(result)
    return render_template(
        "order_result_page.html",
        order_list=order_object,
        nickname=session["member_data"]["nickname"],
        number_list=number_list,
    )


# each_order_function
@app.route("/order")
def order():
    if not "member_data" in session:
        flash("請先登入")
        return redirect("/")
    session["edit"] = "edit"
    phone = request.args.get("phone")  # change into order-number
    result = Order.search(phone)
    session["items"] = [
        ["原味肉粽（無蛋）", result["原味肉粽(無蛋)"], "o_n_item"],
        ["原味肉粽（有蛋）", result["原味肉粽(有蛋)"], "o_item"],
        ["干貝粽", result["干貝粽"], "sc_item"],
        ["干貝鮑魚粽", result["干貝鮑魚粽"], "sc_a_item"],
        ["鹼粽", result["鹼粽"], "a_item"],
        ["紅豆鹼粽", result["紅豆鹼粽"], "b_a_item"],
        ["南部粽", result["南部粽"], "so_item"],
    ]
    session["order-number"] = result["order-number"]
    print(session["items"])
    return render_template(
        "each_order_page.html",
        items=session["items"],
        phone=result["phone"],
        order_number=result["order-number"],
        order_time=result["year"]
        + "-"
        + result["month"]
        + "-"
        + result["day"]
        + "T"
        + result["time"],
        cost=result["cost"],
    )


# check_order
@app.route("/check_order")
def check_order():
    if "member_data" in session:
        phone = request.args.get("phone")
        Order.check(phone)
        flash("取貨成功")
        return redirect("/order_page")
    flash("請先登入")
    return redirect("/")


# delete_order
@app.route("/delete_order", methods=["GET", "POST"])
def delete_order():
    if "member_data" in session:
        phone = request.args.get("phone")
        Order.delete(
            phone, request.headers.get("User-Agent"), request.form["delete_member"]
        )
        flash("刪除成功")
        return redirect("/order_page")
    flash("請先登入")
    print("none")
    return redirect("/")


# edit_price_function
@app.route("/edit_price", methods=["GET", "POST"])
def edit_price():
    session["price"] = [
        ["原味肉粽（無蛋）", int(request.form["o_n_price"]), "o_n_price"],
        ["原味肉粽（有蛋）", int(request.form["o_price"]), "o_price"],
        ["干貝粽", int(request.form["sc_price"]), "sc_price"],
        ["干貝鮑魚粽", int(request.form["sc_a_price"]), "sc_a_price"],
        ["鹼粽", int(request.form["a_price"]), "a_price"],
        ["紅豆鹼粽", int(request.form["b_a_price"]), "b_a_price"],
        ["南部粽", int(request.form["so_price"]), "so_price"],
    ]
    return render_template(
        "add_order_page.html",
        price=session["price"],
        items=session["items"],
        cost=0,
        order_number=session["order-number"],
        each_cost=session["each_cost"],
    )


# finish_order_function
@app.route("/finish_order", methods=["GET", "POST"])
def finish_order():
    if session["edit"] == "edit":
        session["items"] = [
            ["原味肉粽（無蛋）", int(request.form["o_n_item"]), "o_n_item"],
            ["原味肉粽（有蛋）", int(request.form["o_item"]), "o_item"],
            ["干貝粽", int(request.form["sc_item"]), "sc_item"],
            ["干貝鮑魚粽", int(request.form["sc_a_item"]), "sc_a_item"],
            ["鹼粽", int(request.form["a_item"]), "a_item"],
            ["紅豆鹼粽", int(request.form["b_a_item"]), "b_a_item"],
            ["南部粽", int(request.form["so_item"]), "so_item"],
        ]
        Order.change(
            request.form["phone"],
            session["order-number"],
            session["items"],
            request.form["order-time"].replace("T", "-").split("-"),
            request.form["cost"],
            request.headers.get("User-Agent"),
        )
        session["edit"] = "none"
        print(request.form["phone"])
        flash("編輯成功")
        return redirect("/order_page")
    if not "cost" in session:
        flash("尚未小計")
        return render_template(
            "add_order_page.html",
            price=session["price"],
            items=session["items"],
            each_cost=session["each_cost"],
        )
    if not request.form["phone"]:
        flash("請輸入電話號碼")
        return render_template(
            "add_order_page.html",
            price=session["price"],
            items=session["items"],
            each_cost=session["each_cost"],
        )
    print(session)
    if Order.search(session["order-number"]) != None:
        flash("該訂單編號已被使用")
        return redirect("/add_order_page")
    print(session["items"])
    Order.order(
        request.form["phone"],
        session["order-number"],
        session["items"],
        request.form["order-time"].replace("T", "-").split("-"),
        session["cost"],
    )
    flash("訂購成功")
    return redirect("/add_order_page")


@app.route("/cost", methods=["GET", "POST"])
def cost():
    session["items"] = [
        ["原味肉粽（無蛋）", int(request.form["o_n_item"]), "o_n_item"],
        ["原味肉粽（有蛋）", int(request.form["o_item"]), "o_item"],
        ["干貝粽", int(request.form["sc_item"]), "sc_item"],
        ["干貝鮑魚粽", int(request.form["sc_a_item"]), "sc_a_item"],
        ["鹼粽", int(request.form["a_item"]), "a_item"],
        ["紅豆鹼粽", int(request.form["b_a_item"]), "b_a_item"],
        ["南部粽", int(request.form["so_item"]), "so_item"],
    ]
    cost = 0
    for i in range(len(session["items"])):
        cost += session["items"][i][1] * session["price"][i][1]
    for i in range(len(session["each_cost"])):
        session["each_cost"][i][1] = session["items"][i][1] * session["price"][i][1]
    print("cost", cost)
    session["cost"] = cost
    return render_template(
        "add_order_page.html",
        price=session["price"],
        items=session["items"],
        cost=session["cost"],
        order_number=session["order-number"],
        each_cost=session["each_cost"],
    )


@app.route("/secret")
def count_all_cost():
    if (
        session["member_data"]["nickname"] == "TimHu"
        or session["member_data"]["nickname"] == "Yuan"
    ):
        collection = db.order
        result = list(collection.find())
        all_cost = 0
        try:
            for i in result:
                print(i["order-number"], i["cost"])
                each_cost = re.sub(
                    "\\(.*?\\)|\\{.*?\\}|\\[.*?\\]|\\<.*?\\>", "", str(i["cost"])
                )
                all_cost += int(re.sub("[\u4e00-\u9fa5]", "", str(each_cost)))
            return str(all_cost)
        except:
            flash(i["order-number"], i["cost"])
            return redirect("/error?msg=發生錯誤，請稍後再試")
    return "Do not try to know the secret!!"


@app.route("/predict", methods=["POST"])
def predict():
    if "member_data" in session:
        input_text = request.form["input"]
        return jsonify({"predictions": Member.predict_search(input_text)})
    flash("請先登入")
    return redirect("/")


# 咖啡店寄杯功能
@app.route("/coffee_shop_page")
def coffee_shop_page():
    if "member_data" in session:
        return render_template("coffee_shop_page.html")
    flash("請先登入")
    return redirect("/")


@app.route("/phone_check", methods=["POST"])
def phone_check():
    if "member_data" in session:
        data = Coffee.phone_check(request.form["input"])
        print({"phone": data[0], "number": data[1]})
        return jsonify({"phone": data[0], "number": data[1]})
    flash("請先登入")
    return redirect("/")


@app.route("/add_coffee", methods=["POST"])
def add_coffee():
    if "member_data" in session:
        Coffee.add_coffee_function(
            request.form["phone"],
            int(request.form["number"]),
            str(request.form["item"]),
        )
        result = Line.send_notify(request.form["phone"])
        if result != False:
            line_bot_api.push_message(
                result[0],
                TextSendMessage(
                    "寄杯成功通知\n此次寄杯"
                    + request.form["item"]
                    + "元品項共"
                    + request.form["number"]
                    + "杯"
                ),
            )
        Line.save_data(
            request.form["phone"]
            + "寄"
            + request.form["item"]
            + "品項"
            + request.form["number"]
            + "杯"
        )
        flash("寄杯成功")
        return redirect("/coffee_shop_page")
    flash("請先登入")
    return redirect("/")


@app.route("/take_coffee", methods=["POST"])
def take_coffee():
    if "member_data" in session:
        flash(
            Coffee.take_coffee_function(
                request.form["phone"],
                int(request.form["number"]),
                str(request.form["item"]),
            )
        )
        Line.save_data(
            request.form["phone"]
            + "取"
            + request.form["item"]
            + "品項"
            + request.form["number"]
            + "杯"
        )
        result = Line.send_notify(request.form["phone"])
        if result != False:
            line_bot_api.push_message(
                result[0],
                TextSendMessage(
                    "取杯通知\n此次取杯"
                    + request.form["item"]
                    + "元品項共"
                    + request.form["number"]
                    + "杯"
                ),
            )
        return redirect("/coffee_shop_page")
    flash("請先登入")
    return redirect("/")


@app.route("/update_money", methods=["POST"])
def update_money():
    if "member_data" in session:
        flash(
            Money.update_money_function(
                request.form["text"],
                request.form["categories"],
                int(request.form["amount"]),
            )
        )
        return render_template(
            "money.html",
            data=Money.check_money(0, 0),
            balance=Money.count_money(0, 0)[0],
            balance_list=Money.count_money(0, 0)[1],
        )
    return redirect("/")


@app.route("/delete_money")
def delete_money():
    if "member_data" in session:
        flash(Money.delete_money_function(request.args.get("id")))
        return render_template(
            "money.html",
            data=Money.check_money(0, 0),
            balance=Money.count_money(0, 0)[0],
            balance_list=Money.count_money(0, 0)[1],
        )
    flash("請先登入")
    return redirect("/")


# linebot
# 接收 LINE 的資訊
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        if event.message.text == "寄杯查詢":
            result = Line.check_coffee(event.source.user_id)
            if result != False:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        "查詢結果：\n70杯品項剩餘："
                        + str(result["70"])
                        + "杯\n80杯品項剩餘："
                        + str(result["80"])
                        + "杯"
                    ),
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage("查無資料，請稍後再試或確認寄杯狀態")
                )
        if event.message.text.isnumeric() == True:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    Line.bind_phone(event.message.text, event.source.user_id)
                ),
            )
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="很抱歉，您的回覆超出了我的能力範圍")
            )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
