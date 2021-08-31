from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required
    )
import bcrypt
from resources.db import db

BLOCKLIST=set()

_user_parser = reqparse.RequestParser()

_user_parser.add_argument('username',
                          type=str,
                          required=False,
                          help="This field is required for Registration."
                          )
                          
_user_parser.add_argument('email',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )

_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if not data['username']:
            return {"message": "Username missing."}, 404
        elif UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists"}, 400
        elif UserModel.find_by_email(data['email']):
            return {"message": "A user with that email already exists"}, 400

        pswd=data['password']
        hashed_pswd = bcrypt.hashpw(pswd.encode('utf8'), bcrypt.gensalt())
        
        user = UserModel(data['username'], data['email'], hashed_pswd)
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()

        user = UserModel.find_by_email(data['email'])
        pswd=data['password']

        if user and bcrypt.checkpw(pswd.encode('utf8'), user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200

        return {"message": "Invalid Credentials!"}, 401

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        return user.username, 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200
