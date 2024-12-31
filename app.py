from flask import Flask, session, render_template, redirect, url_for, flash, request, abort,jsonify, send_from_directory
from flask_restful import Api
from resources.login import *
from resources.function import *
from resources.func_linebot import *
from resources.qrcode_api import *
from dotenv import load_dotenv
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,FlexSendMessage
import google.auth.transport.requests
import os,certifi,pymongo

load_dotenv()

# 初始化資料庫連線
client = pymongo.MongoClient(
    "mongodb+srv://" + os.getenv("mongodb") + ".rpebx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=certifi.where(),
)
db = client.order_system_v2
users = db["users"]
customer = db["customer"]
coffee = db["coffee"]
print("\x1b[6;30;42m" + "資料庫連線成功".center(87) + "\x1b[0m")

app = Flask(__name__)
app.secret_key = os.getenv("secret_key")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = os.getenv("OAUTHLIB_INSECURE_TRANSPORT")
GOOGLE_OAUTH_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [
            os.getenv("GOOGLE_REDIRECT_URI")
        ]
    }
}

# OAuth 2.0 Flow
flow = Flow.from_client_config(
    GOOGLE_OAUTH_CONFIG, scopes=["https://www.googleapis.com/auth/userinfo.profile",
                                 "https://www.googleapis.com/auth/userinfo.email", "openid"]
)
flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

# Line Bot
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)



# 登入檢查裝飾器
def login_required(func):
    def wrapper(*args, **kwargs):
        if "username" in session:
            return func(*args, **kwargs)
        else:
            flash("請先登入")
            return redirect("/login")
    return wrapper


# Google 登入
@app.route("/google-login")
def google_login():
    session.clear()
    authorization_url, state = flow.authorization_url()
    print(f"Authorization URL: {authorization_url}")
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    print(f"Callback triggered. Request args: {request.args}")
    try:
        if "state" not in session or session["state"] != request.args.get("state"):
            return "Error: 無效的 state 參數！請重新登入。", 400

        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        request_session = google.auth.transport.requests.Request()
        id_info = id_token.verify_oauth2_token(credentials.id_token, request_session)

        user_email = id_info.get("email")
        user_name = id_info.get("name")

        session["username"] = user_email
        session["name"] = user_name
        session["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not users.find_one({"username": user_email}):
            return "Error: 無效的帳號！請註冊後再試一次。", 400

        return redirect(url_for("home"))
    except Exception as e:
        session.clear()
        print(f"Error during callback: {e}")
        return f"登入失敗，請重新嘗試。錯誤訊息：{str(e)}", 400

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# 加載 API
api = Api(app)
api.add_resource(LoginResource, "/login", resource_class_kwargs={"users": users})
api.add_resource(LogoutResource, "/logout")
api.add_resource(RegisterResource, "/register", resource_class_kwargs={"users": users})
api.add_resource(CustomerResource, "/api/customer", resource_class_kwargs={"customer": customer})
api.add_resource(CoffeeResource, "/api/coffee", resource_class_kwargs={"coffee": coffee})


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)  # 設定 session 的有效期限


@app.route("/")
def home():
    return render_template('logo.html')


@app.route("/page/<template>")
@login_required
def page(template):
    if template != None or template != "":
        try:
            return render_template(template + ".html")
        except:
            return render_template("error.html")
    return render_template("home.html")

@app.route('/qrcodes/<filename>')
def serve_qrcode(filename):
    return send_from_directory(QR_DIR, filename)


@app.route("/linebot-callback", methods=['POST'])
def linebot_callback():
    # 確認 X-Line-Signature
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print(f"Request body: {body}")  # Debug 用

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route("/linebot-push", methods=['GET'])
def linebot_push():
    try:
        user_id=coffee.find_one({'phone':request.args.get("phone")})['line_id']
        try:
            message = FlexSendMessage(alt_text="這是 Flex Message", contents=json.loads(push_flex_message(request.args.get("function"),request.args.get("item"),request.args.get("number"))))
            line_bot_api.push_message(user_id, message)
            return 'success', 200
        except Exception as e:
            return f"Error sending bubble message: {e}" , 400
    except:
        return 'no_line_id', 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 從 func_linebot.py 獲取回覆訊息的 JSON 結構
    response_json = generate_message_template(event.message.text,event.source.user_id)
    response = json.loads(response_json)

    # 判斷回傳的訊息類型並回覆
    if response.get("type") == "text":
        # 如果是文字訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response["text"])
        )
    elif response.get("type") == "bubble":
        # 如果是 Flex Message
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="這是 Flex Message", contents=response)
        )
    else:
        # 如果回傳的結構未識別
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="發生錯誤：無法識別的訊息格式")
        )



if __name__ == "__main__":
    app.run(debug=True, port=5500, host="0.0.0.0")