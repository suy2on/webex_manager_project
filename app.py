from flask import Flask, render_template, jsonify, request, redirect, session
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from flask import session
#import os
#from models import db, User

app = Flask(__name__)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta  # 'dbsparta'라는 이름의 db를 만들거나 사용합니다.


## HTML을 주는 부분


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    userid = session.get('userid', None)
    print(userid['userid'])
    return render_template('home.html', realuser=userid['userid'])

@app.route('/classroom')
def classroom():
    userid = session.get('userid', None)
    return render_template('class.html', realuser=userid['userid'])

@app.route('/join', methods=['GET'])
def user_info():
    all_users = list(db.register.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!','data':all_users})


@app.route('/join', methods=['POST'])
def join():
    # 가입정보 넘겨받기
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    email_receive= request.form['email_give']
    print(id_receive)

    #받은정보 db에 저장
    doc={'userid': id_receive,
         'userpw': pw_receive,
         'useremail': email_receive
         }
    doc2={ 'userid':id_receive,
        'classname':[],
        'classurl':{}
    }
    db.register.insert_one(doc)
    db.manage.insert_one(doc2)

    #db에저장
    #user = User()
    #user.password = pw_receive
    #user.userid = id_receive
    #user.username = name_receive
    #db.session.add(user)
    #db.session.commit()

    return jsonify({'result': 'success', 'msg': '회원가입완료!'})



@app.route('/login', methods=['GET','POST'])
def login():
    #db에서 로그인한 user의 이름가져오기
    id_receive=request.form['id_give']
    pw_receive=request.form['pw_give']

    user = db.register.find_one({'userid': id_receive}, {'_id': False})

    if user['userpw']==pw_receive:
        session['userid'] = user
        print('true')
        # return render_template('/home', realuser=user['userid'])
        return jsonify({'result': 'success', 'msg': '로그인 성공'})
    else:
        return jsonify({'result': 'false', 'msg': '아이디와 비밀번호가 일치하지 않습니다'})

@app.route('/class', methods=['POST'])
def add_class():
    class_receive=request.form['class_give']
    url_receive=request.form['url_give']
    id = session.get('userid', None)['userid']

    #db에서 add를 요청한 user의 기존 class data가져오기
    user = db.manage.find_one({'userid': id}, {'_id': False})
    classname=user['classname'] #classname list
    classurl=user['classurl']  #classurl dic

    classname.append(class_receive) #classname list에 추가
    classurl[class_receive]=url_receive #classurl dic에 key:value 추가

    db.manage.update_one({'userid': id}, {'$set': {'classname': classname }})
    db.manage.update_one({'userid': id}, {'$set': {'classurl': classurl}})

    return jsonify({'result': 'success', 'msg': '강의추가완료'})

@app.route('/class2', methods=['POST'])
def delete_class():
    classname_receive=request.form['classname_give']
    id = session.get('userid', None)['userid']

    #db에서 요청한 유저의 기존데이터가져오기
    user = db.manage.find_one({'userid': id}, {'_id': False})
    classname = user['classname']  # classname list
    classurl = user['classurl']  # classurl dic
    #수정
    classname.remove(classname_receive)
    del classurl[classname_receive]
    #db에 다시 update
    db.manage.update_one({'userid': id}, {'$set': {'classname': classname}})
    db.manage.update_one({'userid': id}, {'$set': {'classurl': classurl}})

    return jsonify({'result': 'success', 'msg': '강의삭제완료'})

@app.route('/class', methods=['GET'])
def show_class():
    id = session.get('userid', None)['userid']
    #db에서 가져와서 넘겨주기
    user = db.manage.find_one({'userid': id}, {'_id': False})
    print(user)
    classname = user['classname']  # classname list
    classurl = user['classurl']  # classurl dic

    return jsonify({'result': 'success', 'classname': classname, 'classurl': classurl})

if __name__ == '__main__':
    #dbfile = os.path.join(basedir, 'db.sqlite')  # 데이터베이스 이름과 경로
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    #app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 사용자에게 원하는 정보를 전달완료했을때가 TEARDOWN, 그 순간마다 COMMIT을 하도록 한다.라는 설정
    # 여러가지 쌓아져있던 동작들을 Commit을 해주어야 데이터베이스에 반영됨. 이러한 단위들은 트렌젝션이라고함.
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # True하면 warrnig메시지 유발,

    #db.init_app(app)  # 초기화 후 db.app에 app으로 명시적으로 넣어줌
    #db.app = app
    #db.create_all()  # 이 명령이 있어야 생성됨. DB가
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'
    app.run('0.0.0.0', port=5000, debug=True)
