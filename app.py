from flask import Flask, render_template, jsonify, request, redirect, session
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
import os
from models import db, User

app = Flask(__name__)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db2 = client.dbsparta  # 'dbsparta'라는 이름의 db를 만들거나 사용합니다.


## HTML을 주는 부분
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/join', methods=['POST'])
def join():
    # 가입정보 넘겨받기
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    print(id_receive)

    # if not (id_receive and name_receive and pw_receive and repw_receive):
    # return "모두 입력해주세요"
    # elif pw_receive != repw_receive:
    # return "비밀번호를 확인해주세요"

    #db에저장
    user = User()
    user.password = pw_receive
    user.userid = id_receive
    user.username = name_receive
    db.session.add(user)
    db.session.commit()

    return jsonify({'result': 'success', 'msg': '회원가입완료!'})


# @app.route('/home', methods=['GET'])
# def user_name():
# db에서 로그인한 user의 이름가져오기
# name
# 이름넘겨주기
# return jsonify({'result': 'success', 'data':name})


if __name__ == '__main__':
    basedir = os.path.abspath(os.path.dirname(__file__))  # database 경로를 절대경로로 설정함
    dbfile = os.path.join(basedir, 'db.sqlite')  # 데이터베이스 이름과 경로
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 사용자에게 원하는 정보를 전달완료했을때가 TEARDOWN, 그 순간마다 COMMIT을 하도록 한다.라는 설정
    # 여러가지 쌓아져있던 동작들을 Commit을 해주어야 데이터베이스에 반영됨. 이러한 단위들은 트렌젝션이라고함.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # True하면 warrnig메시지 유발,

    db.init_app(app)  # 초기화 후 db.app에 app으로 명시적으로 넣어줌
    db.app = app
    db.create_all()  # 이 명령이 있어야 생성됨. DB가

    app.run('0.0.0.0', port=5000, debug=True)
