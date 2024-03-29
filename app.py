from flask import Flask, redirect, request, flash, jsonify
from flask_cors import CORS
from flask_restful import Api
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    JWTManager, jwt_required, set_access_cookies,
    create_access_token, get_jwt, get_jwt_identity )
from datetime import datetime, timedelta, timezone
from resources.security import sha256, hash_gen
from resources.user import BLOCKLIST
from resources.user import UserLogout, UserRegister, UserLogin
from resources.blockf import get_info
from time import sleep
import os
import tx_script as tx


app = Flask(__name__)
api = Api(app)
CORS(app)

UPLOAD_FOLDER = 'uploader'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['JWT_AUTH_URL_RULE'] = '/api/login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = "bruh"


@app.before_first_request
def create_tables():
    db.create_all()

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

jwt=JWTManager(app)

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:   # we should read from a config file to get a list of admins instead
        return {'is_admin': True}
    return {'is_admin': False}

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLOCKLIST


# The following callbacks are used for customizing jwt response/error messages.
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):  # we have to keep the argument here, since it's passed in by the caller internally
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401

# JWT configuration ends


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/verifier', methods = ['POST'])
def verify_file():
   if request.method=='POST':
      if 'file' not in request.files:
            flash('No file part')
            return {"message": "invalid"}
      
      file=request.files['file']
      if file and allowed_file(file.filename):
         filename = secure_filename(file.filename)
         file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/verify', filename))
         check=sha256(UPLOAD_FOLDER+'/verify/'+filename)
         print(check)
         return get_info(check)
      else: return {"message": "Not found"}, 404


@app.route('/api/uploader', methods = ['POST'])
@jwt_required()
async def upload_file():
   if request.method == 'POST':
      if 'files[]' not in request.files:
            flash('No file part')
            return {"message": "invalid" }

      files = request.files.getlist('files[]')

      if len(files)>9:
        file_set=list()
        for file in files:
            if file and allowed_file(file.filename):
               filename = secure_filename(file.filename)
               file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/issue', filename))
               file_set.append(UPLOAD_FOLDER+'/issue/'+filename)
               #hash_set.append(sha256(UPLOAD_FOLDER+'/issue/'+filename))
        hash_set= hash_gen(file_set)
        #print(hash_set)
      else : return {"message": "Submit more than 10 files"}, 406
      
      hash_len=200                  #Max Number of files per tx
      tx_list=[]
      log=open("logs/log.txt","a")
      if len(hash_set)>hash_len:
         hash_list=[hash_set[i:i+hash_len] for i in range(0, len(hash_set), hash_len)]
         #print(hash_list)
         for i in hash_list:
            out= await tx.tx_create(i)
            if out==False:
               return {"message": "Transaction failed"}, 503
            else:
                tx_list.append(out)
                log.write(str(out)+'\n')
            print(out)
            #sleep(1)
      else:
         #print(hash_set)
         out= await tx.tx_create(hash_set)
         print(out)
         if out==False:
            return {"message": "Transaction failed"}, 503
         else: 
             tx_list.append(out)
             log.write(str(out)+'\n')
         hash_set.clear()
      log.close()
      return {"Executed": tx_list}


api.add_resource(UserRegister, '/api/register')
api.add_resource(UserLogin, '/api/login')
api.add_resource(UserLogout, '/api/logout')


if __name__ == '__main__':
   from resources.db import db
   db.init_app(app)
   app.run(debug = True)
