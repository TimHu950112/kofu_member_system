from resources.qrcode_api import generate_qrcode
from datetime import datetime,timedelta
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import os,certifi,pymongo,json

load_dotenv()

client = pymongo.MongoClient(
    "mongodb+srv://" + os.getenv("mongodb") + ".rpebx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=certifi.where(),
)
db = client.order_system_v2
coffee = db["coffee"]

def load_template(name):
    template_path = os.path.join(os.path.dirname(__file__), name)
    with open(template_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_message_template(user_message,user_id):
    if user_message.lower() == "template":
        template = load_template("linebot_template.json")
        return json.dumps(template)
    if user_message == '寄杯查詢':
        result = list(coffee.find({'line_id':user_id}))
        if len(result) == 0 or result == None:
            return json.dumps({
                "type": "text",
                "text": f"尚未完成綁定或查詢異常，請輸入手機號碼後再試一次。"
            }, indent=4)
        else:
            return json.dumps({
                "type": "text",
                "text": "70元品項剩餘："+str(result[0]['left']['70'])+"杯\n"+"80元品項剩餘："+str(result[0]['left']['80'])+'杯'
            }, indent=4)
    elif user_message.isnumeric() and len(user_message) == 10:
        result = coffee.find_one({'phone':user_message})
        if result == None:
            return json.dumps({
                "type": "text",
                "text": "查無此手機號碼，請再試一次。"
            }, indent=4)
        coffee.update_one({'phone': user_message}, {'$set': {'line_id': user_id}})
        return json.dumps({
            "type": "text",
            "text": "手機綁定成功"
        }, indent=4)
    else:
        # 如果不是要求模板，回傳普通文字訊息
        return json.dumps({
            "type": "text",
            "text": f"「{user_message}」無法辨識該指令，請再試一次。"
        }, indent=4)
    
def push_flex_message(function,item,number):
    template = load_template("linebot_template.json")
    if item == '70':
        template['body']['contents'][5]['contents'][1]['contents'][0]['text']='70元品項'
    elif item == '80':
        template['body']['contents'][5]['contents'][1]['contents'][0]['text']='80元品項'
    if function == 'add_coffee':
        template['body']['contents'][5]['contents'][1]['contents'][2]['text']=number
    elif function == 'take_away':
        template['body']['contents'][5]['contents'][1]['contents'][1]['text']=number
    template['body']['contents'][5]['contents'][3]['contents'][1]['text']=number
    template['body']['contents'][6]['contents'][1]['text']='payment_id'
    # template['body']['contents'][5]['contents'][1]['contents'][0]['text']='品項item'
    # template['body']['contents'][5]['contents'][1]['contents'][1]['text']='取杯數量'
    # template['body']['contents'][5]['contents'][1]['contents'][2]['text']='寄杯數量'
    # template['body']['contents'][6]['contents'][1]['text']='payment_id'
    # template['body']['contents'][5]['contents'][3]['contents'][1]['text']='共幾項'
    # template['body']['contents'][5]['contents'][4]['contents'][1]['text']='0元'
    # print(template['body']['contents'][5]['contents'][4]['contents'][1]['text'])
    return json.dumps(template)