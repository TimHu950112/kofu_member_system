from flask import request, session, render_template, make_response, redirect, flash
from flask_restful import Resource
from functools import wraps
import bcrypt,random,string

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            # flash('請先登入')
            return redirect('/index')
        return f(*args, **kwargs)
    return decorated_function

class LoginResource(Resource):
    def __init__(self, **kwargs):
        self.users = kwargs['users']
    
    def get(self):
        response = make_response(render_template('login.html'))
        response.headers['Content-Type'] = 'text/html'
        return response

    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = self.users.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = username
            return flash('登入成功'), 200
        else:
            return {'message': '帳號或密碼錯誤'}, 401

class LogoutResource(Resource):
    @login_required
    def get(self):
        session.clear()
        flash('登出成功')
        response = make_response(render_template('login.html'))
        response.headers['Content-Type'] = 'text/html'
        return response
    

class RegisterResource(Resource):
    def __init__(self, **kwargs):
            self.users = kwargs['users']
            
    @login_required
    def get(self):
        
        response = make_response(render_template('register.html'))
        response.headers['Content-Type'] = 'text/html'
        return response
    
    @login_required
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 檢查是否有重複的使用者名稱
        if self.users.find_one({'username': username}):
            return {'message': '用戶名稱已經存在'}, 400

        # 將密碼進行 bcrypt 雜湊處理
        hashed_password =  bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


        # 將使用者資料存入 MongoDB
        self.users.insert_one({'username': username, 'password': hashed_password})

        return {'message': '註冊成功，請登入'}, 201



    