from flask import request, session, render_template, make_response, redirect, flash
from flask_restful import Resource
from functools import wraps
from datetime import datetime
import pytz

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            # flash('請先登入')
            return redirect('/index')
        return f(*args, **kwargs)
    return decorated_function

class CustomerResource(Resource):
    def __init__(self, **kwargs):
        self.customer = kwargs['customer']
    
    @login_required
    def get(self):
        data = request.args.get('phone')
        phone = data
        result = []
        for i in self.customer.find({'phone':{'$regex':phone}}):
            result.append({'phone':i['phone'],'name':i['name'],'permanent_status':i['permanent_status'],'active_year':i['active_year']})
        return result, 200

    @login_required
    def post(self):
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone')
        permanent_status = data.get('permanent_status')
        result = self.customer.find_one({'phone':phone})
        if result != None:
            self.customer.update_one({'phone':phone},{'$set':{'active_year':datetime.now(pytz.timezone("Asia/Taipei")).year,'permanent_status':permanent_status}})
            return {'message': 'updated'}, 200
        else:
            self.customer.insert_one({'name':name,'phone':phone,'permanent_status':permanent_status,'active_year':datetime.now(pytz.timezone("Asia/Taipei")).year})
            return {'message': 'added'}, 200
    

class CoffeeResource(Resource):
    def __init__(self, **kwargs):
        self.coffee = kwargs['coffee']

    @login_required
    def get(self):
        data = request.args.get('phone')
        phone = data
        result = []
        for i in self.coffee.find({'phone':{'$regex':phone}}):
            result.append({'phone':i['phone'],'left':i['left']})
        return result, 200


    @login_required
    def post(self):
        data = request.get_json()
        phone = data.get('phone')
        function = data.get('function')
        item = int(data.get('item'))
        number = int(data.get('number'))
        result = self.coffee.find_one({'phone':phone})
        if result != None and len(result)!=0:
            if function == 'add_coffee':
                self.coffee.update_one({'phone':phone},{'$set':{'left.'+str(item):result['left'][str(item)]+number}})
            elif function == 'take_away':
                self.coffee.update_one({'phone':phone},{'$set':{'left.'+str(item):result['left'][str(item)]-number}})
            else:
                return {'message':'function error'}, 400
            return {'message':'updated'}, 200
        else:
            if function == 'add_coffee':
                if item == 70:
                    self.coffee.insert_one({'phone':phone,'left':{str(item):number,'80':0}})
                elif item == 80:
                    self.coffee.insert_one({'phone':phone,'left':{'70':0,str(item):number}})
                else:
                    return {'message':'item error'}, 400
                return {'message':'added'}, 200
            else:
                return {'message':'function error'}, 400
# 資料庫架構
# {
#     'phone':'',
#     'coffee_list':{'item1':0,'item2':},
#     'line_id':'',
#     'log':[
#         {
#             'time':'',
#             'coffee_list':['item1':0,'item2':0]
#         }
#     ]
# }
