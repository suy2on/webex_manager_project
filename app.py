from flask import Flask, render_template, jsonify, request, redirect
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from flask import session
import bcrypt

# import os
# from models import db, User

app = Flask(__name__)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta  # 'dbsparta'라는 이름의 db를 만들거나 사용합니다.


## HTML을 주는 부분


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/home')
def home():
    user = session.get('user', None)
    print(user['userid'])
    return render_template('home.html', realuser=user['userid'])


@app.route('/classroom')
def classroom():
    user = session.get('user', None)
    return render_template('class.html', realuser=user['userid'])

@app.route('/homework')
def homework():
    user = session.get('user', None)
    return render_template('homework.html', realuser=user['userid'])

#@app.route('/join', methods=['GET'])
#def user_info():
 #   all_users = list(db.register.find({}, {'_id': False}))

  #  return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!', 'data': all_users})

@app.route('/exist', methods=['POST'])
def exist_id():
    id_receive=request.form['id_give']

    all_users = list(db.register.find({}, {'_id': False})) #그대로 데이터 넘겨주면 안된다
    # 비밀번호가 binary암호로 json화 될수 없음

    #여기서 비교후 결과만 반환하는걸로
    for user in all_users:
        if (user['userid'] == id_receive) :
            return jsonify({'result': 'exist'})

    return jsonify({'result': 'pass'})

@app.route('/join', methods=['POST'])
def join():
    # 가입정보 넘겨받기
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    email_receive = request.form['email_give']
    print(id_receive)

    pw_receive= bcrypt.hashpw(pw_receive.encode('utf-8'), bcrypt.gensalt())
    # 받은정보 db에 저장
    doc = {'userid': id_receive,
           'userpw': pw_receive,
           'useremail': email_receive
           }
    doc2 = {'userid': id_receive,
            'classname': [],
            'classurl': {}
            }
    doc3 = {'userid': id_receive,
            'subject': [],
            'hw': {}
            }
    db.register.insert_one(doc)
    db.manage.insert_one(doc2)
    db.manageHW.insert_one(doc3)

    return jsonify({'result': 'success', 'msg': '회원가입완료!'})


@app.route('/login', methods=[ 'POST'])
def login():
    # db에서 로그인한 user의 이름가져오기
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    user = db.register.find_one({'userid': id_receive}, {'_id': False})

    bcrypt.checkpw(pw_receive.encode('utf-8'), user['userpw'] )

    if bcrypt.checkpw(pw_receive.encode('utf-8'), user['userpw'] ):
        session['user'] = user  # session에 로그인 한 사람의 register정보 저장

        return jsonify({'result': 'success', 'msg': '로그인 성공'})
    else:
        return jsonify({'result': 'false', 'msg': '아이디와 비밀번호가 일치하지 않습니다'})

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user',None)
    return jsonify({'result': 'success', 'msg': '로그아웃 성공'})


@app.route('/class', methods=['POST'])
def add_class():
    class_receive = request.form['class_give']
    url_receive = request.form['url_give']
    id = session.get('user', None)['userid']

    # db에서 add를 요청한 user의 기존 class data가져오기
    user = db.manage.find_one({'userid': id}, {'_id': False})
    classname = user['classname']  # classname list
    classurl = user['classurl']  # classurl dic

    classname.append(class_receive)  # classname list에 추가
    classurl[class_receive] = url_receive  # classurl dic에 key:value 추가

    db.manage.update_one({'userid': id}, {'$set': {'classname': classname}})
    db.manage.update_one({'userid': id}, {'$set': {'classurl': classurl}})

    return jsonify({'result': 'success', 'msg': '강의추가완료'})


@app.route('/class2', methods=['POST'])
def delete_class():
    classname_receive = request.form['classname_give']
    id = session.get('user', None)['userid']

    # db에서 요청한 유저의 기존데이터가져오기
    user = db.manage.find_one({'userid': id}, {'_id': False})
    classname = user['classname']  # classname list
    classurl = user['classurl']  # classurl dic
    # 수정
    classname.remove(classname_receive)
    del classurl[classname_receive]
    # db에 다시 update
    db.manage.update_one({'userid': id}, {'$set': {'classname': classname}})
    db.manage.update_one({'userid': id}, {'$set': {'classurl': classurl}})

    return jsonify({'result': 'success', 'msg': '강의삭제완료'})


@app.route('/class', methods=['GET'])
def show_class():
    id = session.get('user', None)['userid']
    # db에서 가져와서 넘겨주기
    user = db.manage.find_one({'userid': id}, {'_id': False})
    print(user)
    classname = user['classname']  # classname list
    classurl = user['classurl']  # classurl dic

    return jsonify({'result': 'success', 'classname': classname, 'classurl': classurl})



@app.route('/hw', methods=['GET'])
def show_hw():
    id = session.get('user', None)['userid']
    # db에서 가져와서 넘겨주기
    user = db.manageHW.find_one({'userid': id}, {'_id': False})
    print(user)
    subject = user['subject']  # subject name list
    hw = user['hw']  # hw dict

    return jsonify({'result': 'success', 'subject': subject, 'hw': hw})




@app.route('/addsub', methods=['POST'])
def add_subject():
    subject_receive = request.form['subject_give']
    id = session.get('user', None)['userid']

    # db에서 요청한 user의 정보가져오기
    user = db.manageHW.find_one({'userid': id}, {'_id': False})
    subject = user['subject']  # subject list
    hw=user['hw'] #hw dict

    # 수정 및 update
    subject.append(subject_receive)  # classname list에 추가
    hw[subject_receive]=[]
    db.manageHW.update_one({'userid': id}, {'$set': {'subject': subject}})
    db.manageHW.update_one({'userid': id}, {'$set': {'hw': hw}})

    return jsonify({'result': 'success', 'msg': '과목추가완료'})

@app.route('/delsub', methods=['POST'])
def del_subject():
    subject_receive = request.form['subject_give']
    id = session.get('user', None)['userid']

    # db에서 요청한 유저의 기존데이터가져오기
    user = db.manageHW.find_one({'userid': id}, {'_id': False})
    subject = user['subject']  # subject list
    hw= user['hw']  # hw dic


    #hw에 subject key가 있다면 없애기
    if subject_receive in hw.keys():
        del hw[subject_receive] #if문 없으면 오류
        db.manageHW.update_one({'userid': id}, {'$set': {'hw': hw}})
    #과목없애기
    subject.remove(subject_receive)
    db.manageHW.update_one({'userid': id}, {'$set': {'subject': subject}})


    return jsonify({'result': 'success', 'msg': '과목삭제완료'})



@app.route('/addhw', methods=['POST'])
def add_hw():
    subject_receive = request.form['subject_give']
    main_receive = request.form['main_give']
    sub_receive = request.form['sub_give']
    day_receive = request.form['day_give']
    id = session.get('user', None)['userid']

    # db에서 회원정보가져오기
    user = db.manageHW.find_one({'userid': id}, {'_id': False})
    hw = user['hw']  # hw dict


    doc={
        'main':main_receive,
        'sub':sub_receive,
        'day':day_receive
    }

    #수정 및 update
    hw[subject_receive].append(doc)
    db.manageHW.update_one({'userid': id}, {'$set': {'hw': hw}})

    return jsonify({'result': 'success', 'msg': '과제추가완료'})

@app.route('/delhw', methods=['POST'])
def del_hw():
    subject_receive = request.form['subject_give']
    index_receive = request.form['index_give']
    id = session.get('user', None)['userid']


    # db에서 요청한 유저의 기존데이터가져오기
    user = db.manageHW.find_one({'userid': id}, {'_id': False})
    hw = user['hw']  # hw dic

    # 수정
    del hw[subject_receive][int(index_receive)]
    # db에 다시 update
    db.manageHW.update_one({'userid': id}, {'$set': {'hw': hw}})

    return jsonify({'result': 'success', 'msg': '과제삭제완료'})



if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'
    app.run('0.0.0.0', port=5000, debug=True)
