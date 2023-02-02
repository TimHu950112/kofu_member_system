from crypt import methods
from imp import reload
from flask import*
from unittest import result
import pymongo
import certifi
from requests import Session

#導入物件設定
from data import*

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

#index_page
@app.route("/")
def index():
    session.clear()
    print(session)
    return render_template("login.html")

#error_page
@app.route("/error")
def error():
    message=request.args.get("msg","發生錯誤，請聯繫客服")
    return render_template("error.html",message=message)

#add_member_page
@app.route("/add_page")
def add_page():
    if "member_data" in session:
        nickname=session["member_data"]["nickname"]
        return render_template("check_old.html",nickname=nickname)
    flash("請先登入")
    return render_template("login.html")

#function_page
@app.route("/function")
def function():
    if "member_data" in session:
        return render_template("function.html")
    flash("請先登入")
    return render_template("login.html")

#search_order_page
@app.route("/order_page")
def order_page():
    if "member_data" in session:
        nickname=session["member_data"]["nickname"]
        return render_template("order_page.html",nickname=nickname)
    flash("請先登入")
    return redirect("/")

#add_order_page
@app.route("/add_order_page")
def add_order_page():
    session["edit"]="none"
    session["price"]=[["原味肉粽（無蛋）",80,"o_n_price"],["原味肉粽（有蛋）",80,"o_price"],["干貝粽",80,"sc_price"],["干貝鮑魚粽",80,"sc_a_price"],["鹼粽",80,"a_price"],["紅豆鹼粽",80,"b_a_price"],["南部粽",80,"so_price"]]
    session["items"]=[["原味肉粽（無蛋）",0,"o_n_item"],["原味肉粽（有蛋）",0,"o_item"],["干貝粽",0,"sc_item"],["干貝鮑魚粽",0,"sc_a_item"],["鹼粽",0,"a_item"],["紅豆鹼粽",0,"b_a_item"],["南部粽",0,"so_item"]]
    return render_template("add_order_page.html",price=session["price"],items=session["items"],cost=0)

#login_function
@app.route("/login",methods=["GET","POST"])
def login():
    session["member_data"]={"email":request.form["email"],"password":request.form["password"]}
    session["member_data"]["nickname"]=User.login(session["member_data"]["email"],session["member_data"]["password"])
    if session["member_data"]["nickname"]== False:
        return redirect("/error?msg=帳號或密碼錯誤")
    return render_template("function.html")

#logout_funtion
@app.route("/logout")
def logout():
    session.clear()
    flash("登出成功")
    return redirect("/")

#check_add_member_function
#To check if he is old member or already a new member
@app.route("/check_old",methods=["GET","POST"])
def check_old():
    session["phone"]=request.form["phone"]
    member_status=Member.check("add",session["phone"])
    print(member_status)
    if member_status==True:
        flash("已經是新會員")
        return render_template("check_old.html")
    if member_status==None:
        return render_template("add_new.html",phone=session["phone"],member_name="請輸入名稱")
    flash("舊會員"+member_status+"請確認是否註冊為永久會員")
    return render_template("add_new.html",phone=session["phone"],member_name=member_status)

#add_member_function
#To add member to mongodb 
@app.route("/add",methods=["GET","POST"])
def add():
    if request.form.get("forever")=="forever":
        forever="forever"
    else:
        forever="not"
    Member.add(request.form["phone"],request.form["member_name"],forever)
    flash("會員註冊成功")
    return render_template("check_old.html")

    
#search_member_function
@app.route("/search",methods=["GET","POST"])
def search():
    status=Member.check("search",request.form["phone"])
    if status==False:
        flash("查無資料")
        return render_template("function.html",status="無資料")
    return render_template("function.html",status=status)

#search_order_function
@app.route("/search_order",methods=["GET","POST"])
def search_order():
    collection=db.order
    if request.form['item'] =="請選取搜尋方式":
        flash("請選擇搜尋方式")
        return redirect("/order_page")
    if request.form['item']=="order-number":
        result=list(collection.find({"order-number":request.form['phone']}))
    if request.form['item']=="phone":
        result=list(collection.find({"phone":request.form['phone']}))
    if request.form['item']=="date":
        date=request.form['phone'].split("-")
        result=list(collection.find({
            "$and":[
                {"year":date[0]},
                {"month":date[1]},
                {"day":date[2]}
            ]
        }))
    if request.form['item']=="number":
        order_object=[]
        result=list(collection.find())
        
    order_object=[]
    for i in range(len(result)):
        order_object.append(Order(result[i]["phone"],result[i]["order-number"],{"原味肉粽(無蛋)":result[i]["原味肉粽(無蛋)"],"原味肉粽(有蛋)":result[i]["原味肉粽(有蛋)"],"干貝粽":result[i]["干貝粽"],"干貝鮑魚粽":result[i]["干貝鮑魚粽"],"鹼粽":result[i]["鹼粽"],"紅豆鹼粽":result[i]["紅豆鹼粽"],"南部粽":result[i]["南部粽"]},result[i]["year"]+"-"+result[i]["month"]+"-"+result[i]["day"]+" "+result[i]["time"],result[i]["status"]))
        number_list=[0,0,0,0,0,0,0]
    for i in range(len(order_object)):
        number_list[0]+=int(order_object[i].items['原味肉粽(無蛋)'])
        number_list[1]+=int(order_object[i].items['原味肉粽(有蛋)'])
        number_list[2]+=int(order_object[i].items['干貝粽'])
        number_list[3]+=int(order_object[0].items['干貝鮑魚粽'])
        number_list[4]+=int(order_object[0].items['鹼粽'])
        number_list[5]+=int(order_object[0].items['紅豆鹼粽'])
        number_list[6]+=int(order_object[0].items['南部粽'])
    try:
        print(number_list)
    except:
        number_list=[0,0,0,0,0,0,0]
    return render_template("order_result_page.html",order_list=order_object,nickname=session["member_data"]["nickname"],number_list=number_list)


#each_order_function
@app.route("/order")
def order():
    session["edit"]="edit"
    phone=request.args.get("phone")
    result=Order.search(phone)
    print(Order.search(phone))
    session["items"]=[["原味肉粽（無蛋）",result["原味肉粽(無蛋)"],"o_n_item"],["原味肉粽（有蛋）",result["原味肉粽(有蛋)"],"o_item"],["干貝粽",result["干貝粽"],"sc_item"],["干貝鮑魚粽",result["干貝鮑魚粽"],"sc_a_item"],["鹼粽",result["鹼粽"],"a_item"],["紅豆鹼粽",result["紅豆鹼粽"],"b_a_item"],["南部粽",result["南部粽"],"so_item"]]
    print(session["items"])
    return render_template("each_order_page.html",items=session["items"],phone=result["phone"],order_number=result["order-number"],order_time=result["year"]+"-"+result["month"]+"-"+result["day"]+"T"+result["time"])

#check_order
@app.route("/check_order")
def check_order():
    phone=request.args.get("phone")
    Order.check(phone)
    flash("取貨成功")
    return render_template("order_page.html")

#delete_order
@app.route("/delete_order")
def delete_order():
    phone=request.args.get("phone")
    Order.delete(phone)
    flash("刪除成功")
    return render_template("order_page.html")

#edit_price_function
@app.route("/edit_price", methods=["GET","POST"])
def edit_price():
    session["price"]=[["原味肉粽（無蛋）",int(request.form["o_n_price"]),"o_n_price"],["原味肉粽（有蛋）",int(request.form["o_price"]),"o_price"],["干貝粽",int(request.form["sc_price"]),"sc_price"],["干貝鮑魚粽",int(request.form["sc_a_price"]),"sc_a_price"],["鹼粽",int(request.form["a_price"]),"a_price"],["紅豆鹼粽",int(request.form["b_a_price"]),"b_a_price"],["南部粽",int(request.form["so_price"]),"so_price"]]
    return render_template("add_order_page.html",price=session["price"],items=session["items"],cost=0)
#finish_order_function
@app.route("/finish_order", methods=["GET","POST"])
def finish_order():
    if not request.form["phone"]:
        flash("請輸入電話號碼")
        return render_template("add_order_page.html",price=session["price"],items=session["items"])
    if not request.form["order-number"]:
        flash("請輸入電話號碼")
        return render_template("add_order_page.html",price=session["price"],items=session["items"])
    if session["edit"]=="edit":
        session["items"]=[["原味肉粽（無蛋）",int(request.form["o_n_item"]),"o_n_item"],["原味肉粽（有蛋）",int(request.form["o_item"]),"o_item"],["干貝粽",int(request.form["sc_item"]),"sc_item"],["干貝鮑魚粽",int(request.form["sc_a_item"]),"sc_a_item"],["鹼粽",int(request.form["a_item"]),"a_item"],["紅豆鹼粽",int(request.form["b_a_item"]),"b_a_item"],["南部粽",int(request.form["so_item"]),"so_item"]]
        Order.change(request.form["phone"],request.form["order-number"],session["items"],request.form['order-time'].replace("T","-").split("-"))
        session["edit"]="none"
        flash("編輯成功")
        return render_template("order_page.html") 
    if Order.search(request.form["phone"])!=None:
        flash("該電話已被使用，請至編輯頁面添加訂單")
        return redirect("/order?phone="+request.form["phone"])
    print(session["items"])
    Order.order(request.form["phone"],request.form["order-number"],session["items"],request.form['order-time'].replace("T","-").split("-"))
    flash("訂購成功")
    return redirect("/add_order_page")

@app.route("/cost", methods=["GET","POST"])
def cost():
    session["items"]=[["原味肉粽（無蛋）",int(request.form["o_n_item"]),"o_n_item"],["原味肉粽（有蛋）",int(request.form["o_item"]),"o_item"],["干貝粽",int(request.form["sc_item"]),"sc_item"],["干貝鮑魚粽",int(request.form["sc_a_item"]),"sc_a_item"],["鹼粽",int(request.form["a_item"]),"a_item"],["紅豆鹼粽",int(request.form["b_a_item"]),"b_a_item"],["南部粽",int(request.form["so_item"]),"so_item"]]
    cost=0
    for i in range(len(session["items"])):
        cost+=session["items"][i][1]*session["price"][i][1]
    print("cost",cost)
    return render_template("add_order_page.html",price=session["price"],items=session["items"],cost=cost)
if __name__=='__main__':
    app.run(port=5000,debug=True)