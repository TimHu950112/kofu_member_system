from flask import*
from dotenv import load_dotenv
import pymongo,certifi,os

load_dotenv()

#初始化資料庫連線
client=pymongo.MongoClient("mongodb+srv://"+os.getenv("mongodb")+".rpebx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=certifi.where())
db=client.kofu_member_system
print("\n"+'\x1b[6;30;42m' + '資料庫連線成功'.center(87) + '\x1b[0m'+"\n")

#初始化 flask 伺服器
app=Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)
app.secret_key=os.getenv("secret_key")


class Order:
    def __init__(self,phone,number,items,date):
        self.phone=phone
        self.number=number
        self.items=items
        self.date=date
class User:
    def __init__(self,nickname,email,password):
        self.nickname=nickname
        self.email=email
        self.password=password


@app.route("/")
def index():
    session.clear()
    # order_1=Order("0979928770","001",{"原味":20,"干貝":10})
    # order_2=Order("0989643006","002",{"原味":30,"干貝":20})
    # test=[order_1.__dict__,order_2.__dict__]
    # session["test"]=test
    # print(session["test"])
    collection=db.order
    result=list(collection.find())
    order_object=[]
    for i in range(len(result)):
        print(i)
        order_object.append(Order(result[i]["phone"],result[i]["order-number"],{"原味肉粽":result[i]["原味肉粽"],"干貝粽":result[i]["干貝粽"],"干貝鮑魚粽":result[i]["干貝鮑魚粽"],"鹼粽":result[i]["鹼粽"]},result[i]["date"]["year"]+"-"+result[i]["date"]["month"]+"-"+result[i]["date"]["day"]+" "+result[i]["date"]["time"]))
    return render_template("white.html",order_list=order_object)

class Price:
    def __init__(self,a,b,c):
        self.a=a
        self.b=b
        self.c=c

@app.route("/test")
def test():
    price=[["原味",80],["干貝",80],["干貝鮑魚",80]]
    return render_template("white_2.html",price=price)


if __name__=='__main__':
    app.run(port=5000,debug=True)






