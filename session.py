from flask import Flask,jsonify,make_response,render_template,request,flash,session,redirect,url_for
from datetime import *
import jwt
from functools import wraps
import requests
import json
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123@192.168.99.101:3303/session-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



app.config['SECRET_KEY'] = 'thisisthesecretkey'


class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    rToken = db.Column(db.String(200),unique=True)

    def __init__(self, rToken):
        self.rToken = rToken



@app.route('/sign_in', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data['email'] or not data['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if  data['password']:
        token = jwt.encode({'email':data['email'],'exp':datetime.utcnow()+timedelta(weeks=1)},app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify!',401,{'WWW-Authenticate' : 'Basic realm="Login Required'})

@app.route('/validate', methods=['POST'])
def validate():
    token = None
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']

    if not token:
        return jsonify({'message' : 'Token is missing'}), 401

    invalidT = db.session.query(db.exists().where(RevokedToken.rToken==token)).scalar()
    if invalidT:
        return jsonify({'message' : 'Token is revoked'}), 401

    try:
        data = jwt.decode(token,app.config['SECRET_KEY'])
    except:
        return  jsonify({'message' : 'Token is invalid'}), 401
    return jsonify({'email': data['email']})

@app.route('/refresh', methods=['POST'])
def refresh():
    token = None

    data1 = request.get_json()

    if not data1 or not data1['email']:
        return make_response('Could not find a email', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    email = data1['email']

    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']

    if not token:
        return jsonify({'message' : 'Token is missing'}), 401

    invalidT = db.session.query(db.exists().where(RevokedToken.rToken==token)).scalar()
    if invalidT:
        return jsonify({'message' : 'Token is revoked'}), 401

    try:
        data = jwt.decode(token,app.config['SECRET_KEY'])
    except:
        token = jwt.encode({'email':email,'exp':datetime.utcnow()+timedelta(weeks=1)},app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})

    rToken = RevokedToken( rToken = token )
    db.session.add(rToken)
    db.session.commit()


    email = data['email']
    token = jwt.encode({'email':email,'exp':datetime.utcnow()+timedelta(weeks=1)},app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})

@app.route('/sign_out', methods=['POST'])
def logout():
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']

    if not token:
        return jsonify({'message' : 'Token is missing'}), 401

    invalidT = db.session.query(db.exists().where(RevokedToken.rToken==token)).scalar()
    if invalidT:
        return jsonify({'message' : 'Token is revoked'}), 401


    rToken = RevokedToken( rToken = token )
    db.session.add(rToken)
    db.session.commit()
    return  jsonify({'message' : 'You are out!'}), 200

if __name__ == "__main__":
    db.init_app(app)
    #with app.app_context():
    #    db.create_all()

    app.run(debug = True, host = '0.0.0.0',  port = 3001)
