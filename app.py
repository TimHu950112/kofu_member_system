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

#初始化 flask 伺服器
app=Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)
app.secret_key="any string"

@app.route("/")
def index():
    session["status"]=None
    return render_template("login.html")


@app.route("/member",methods=["GET","POST"])
def member():
    if "nickname" in session:
        nickname=session["nickname"]
        email=session["email"]
        password=session["password"]
        return render_template("member.html",nickname=nickname,email=email,password=password)
    flash("請先登入")
    return render_template("login.html")

@app.route("/function")
def function():
    if "nickname" in session:
        return render_template("function.html")
    flash("請先登入")
    return render_template("login.html")

@app.route("/add_page")
def add_page():
    if "nickname" in session:
        nickname=session["nickname"]
        return render_template("check_old.html",nickname=nickname)
    flash("請先登入")
    return render_template("login.html")

# @app.route("/add",methods=["GET","POST"])
# def add():
#     session["member_name"]=request.form["member_name"]
#     session["phone"]=request.form["phone"]
#     if request.form.get("forever")=="forever":
#         session["forever"]="forever"
#     else:
#         session["forever"]="not"

#     collection=db.user
#     collection.insert_one({
#     "member_name":session["member_name"],
#     "phone":session["phone"],
#     "forever":session["forever"]})
#     return redirect("/add_page")

@app.route("/add",methods=["GET","POST"])
def add():
    session["member_name"]=request.form["member_name"]
    session["phone"]=request.form["phone"]
    if request.form.get("forever")=="forever":
        session["forever"]="forever"
    else:
        session["forever"]="not"

    collection=db.new
    collection.insert_one({
    "member_name":session["member_name"],
    "phone":session["phone"],
    "forever":session["forever"]})
    flash("會員註冊成功")
    return render_template("check_old.html")

@app.route("/check_old",methods=["GET","POST"])
def check_old():
    session["phone"]=request.form["phone"]
    
    collection=db.user
    result=collection.find_one({
        "phone":session["phone"]
    })

    collection=db.new
    result_one=collection.find_one({
        "phone":session["phone"]
    })

    if result_one==None:
        if result==None:
            print("none")
            return render_template("add_new.html",phone=session["phone"],member_name="會員名稱")
        else:
            session["member_name"]=result["member_name"]
            flash("舊會員"+result["member_name"]+"請確認是否註冊為永久會員")
            return render_template("add_new.html",phone=session["phone"],member_name=session["member_name"])
    else:
        flash("已是新會員")
        return render_template("check_old.html")


@app.route("/search",methods=["GET","POST"])
def search():
    session["phone"]=request.form["phone"]
    collection=db.new
    result=collection.find_one({"phone":session["phone"]})
    if result==None:
        flash("查無資料")
        return render_template("function.html",status="無資料")
    else:
        return render_template("function.html",status=result["member_name"])




@app.route("/error")
def error():
    message=request.args.get("msg","發生錯誤，請聯繫客服")
    return render_template("error.html",message=message)


@app.route("/signup_page")
def signup_page():
    session["status"]=None
    return render_template("signup.html")


@app.route("/signup",methods=["GET","POST"])
def signup():
    nickname=request.form["nickname"]
    email=request.form["email"]
    password=request.form["password"]
    session["email"]=email
    session["nickname"]=nickname
    session["password"]=password
    collection=db.members
    if  not(email and password and nickname):
        return redirect("/error?msg=資料不能為空")
    result=collection.find_one({"email":email})
    if result != None:
        return redirect("/error?msg=信箱已經被註冊")
    return redirect("/check")

@app.route("/check",methods=["GET","POST"])
def check():
    key = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(6))
    session["key"]=key
    print(key)  
    if session["status"]=="forget":
        emails=session["email"]=request.form["emails"]
        session["status"]="forget_twice"
    if session["status"]=="forget_twice":
        emails=session["email"]
    else:
        emails="tim20060112@gmail.com"
        nickname=session["nickname"]
    import email.message
    msg=email.message.EmailMessage()
    msg["From"]="eemailcheck9@gmail.com"
    if session["status"]=="forget_twice":
        msg["To"]=session["email"]
    else:
        msg["To"]=emails
    msg["Subject"]="Email驗證"

    msg.add_alternative("<h3>會員系統驗證碼</h3>您的驗證碼為:"+key+" （請勿向他人傳送此驗證碼，驗證碼限時5分鐘）",subtype="html") #HTML信件內容

    acc="eemailcheck9@gmail.com"
    password="qlqflzkffpsypkml"

    #連線到SMTP Server
    import smtplib

    server=smtplib.SMTP_SSL("smtp.gmail.com",465) #建立gmail連驗
    server.login(acc,password)
    server.send_message(msg)
    server.close() #發送完成後關閉連線
    time_1 = time.time()#紀錄當前時間
    session["time_1"]=time_1
    print(time_1)
    print("驗證碼發送成功")
    if session["status"]=="forget_twice":
        return render_template("check.html",emails=emails)
    else:
        return render_template("check.html",nickname=nickname,emails="後台信箱")
    


@app.route("/check_code",methods=["GET","POST"])
def check_code():
    print(type(request.form["key"]))
    print(request.form["key"])
    print(type(session["key"]))
    print(session["key"])
    time_2 = time.time()#紀錄當前時間
    time_interval = time_2 - session["time_1"] #計算時間差
    print(time_interval)
    if  time_interval<300:
        if request.form["key"]== session["key"]:
            if session["status"]=="forget_twice":
                session["status"]="forget_change"
                return render_template("forget_change.html")
            else:
                collection=db.members
                collection.insert_one({
                "nickname":session["nickname"],
                "email":session["email"],
                "password":session["password"]})
                return redirect("/")
        else:
            return redirect("/error?msg=驗證碼錯誤")
    else:
        print("驗證碼失效")
        return redirect("/check")




@app.route("/login",methods=["GET","POST"])
def login():
    email=request.form["email"]
    password=request.form["password"]
    collection=db.members
    result=collection.find_one({
        "$and":[
            {"email":email},
            {"password":password}
        ]
    })
    if result==None:
        return redirect("/error?msg=帳號或密碼錯誤")
    session["nickname"]=result["nickname"]
    session["email"]=result["email"]
    session["password"]=result["password"]
    return redirect("/function")

@app.route("/logout")
def logout():
    del session["nickname"]
    flash("登出成功")
    return redirect("/")

@app.route("/change",methods=["GET","POST"])
def change():
    password=request.form["password"]
    collection=db.members
    if session["status"]=="forget_change":
        result=collection.update_one({
        "email":session["email"]},
        {"$set":{
            "password":password
        }
    })
    else:
        nickname=request.form["nickname"]
        previous_email=session["email"]
        email=request.form["email"]
        result=collection.find_one({"email":email})
        if email!=previous_email:
            if result != None:
                return redirect("/error?msg=信箱已經被註冊")
        result=collection.update_one({
            "email":previous_email},
            {"$set":{
                "email":email,
                "nickname":nickname,
                "password":password
            }
        })
        print("符合篩選條件數:",result.matched_count)
        print("實際更新資料數:",result.modified_count)
    return redirect("/")
     
@app.route("/forget_page")
def forget_page():
    session["status"]="forget"
    return render_template("forget.html")



app.run(port=5000)






