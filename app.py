from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

app = Flask(__name__)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta  # 'dbsparta'라는 이름의 db를 만들거나 사용합니다.



## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')



@app.route('/join', methods=['GET'])
def user_data():
    #db에서 회원정보가져오기
    all_users= list(db.users.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!', 'data': all_users})

@app.route('/join', methods=['POST'])
def add_id():
    # 가입정보 넘겨받기
    id_receive=request.form['id_give']
    name_receive=request.form['name_give']
    # 넘겨받은 정보 db에 저장
    doc = {
        'id': id_receive,
        'name': name_receive,
        'subject_url': {},
        'subject_name': [],
        'subject_hw': {},
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success', 'msg': 'POST 연결되었습니다!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)