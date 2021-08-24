from flask import Flask, render_template, request, redirect, flash
from flask_cors import CORS
from flask_restful import Api
from werkzeug.utils import secure_filename
from flask_jwt import JWT, jwt_required, current_identity
from security import authenticate, identity, sha256
from user import UserRegister
from blockf import get_info
from time import sleep
import os
import tx_script as tx


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploader'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JWT_AUTH_URL_RULE'] = '/api/login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = "aslkfhlsakdfjhlsakf"
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt=JWT(app,authenticate,identity)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/invalid')
def inv():
   return 'Invalid input. Upload only .pdf certificates.'


@app.route('/api/verifier', methods = ['POST'])
def verify_file():
   if request.method=='POST':
      if 'file' not in request.files:
            flash('No file part')
            return redirect('/invalid')
      
      file=request.files['file']
      if file and allowed_file(file.filename):
         filename = secure_filename(file.filename)
         file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/verify', filename))
         check=sha256(UPLOAD_FOLDER+'/verify/'+filename)
         print(check)
         return get_info(check)
      else: return "Not found"

@app.route('/api/uploader', methods = ['POST'])
@jwt_required()
def upload_file():
   if request.method == 'POST':
      if 'files[]' not in request.files:
            flash('No file part')
            return redirect('/invalid')

      files = request.files.getlist('files[]')

      if len(files)>9:
         hash_set=[]
         for file in files:
            if file and allowed_file(file.filename):
               filename = secure_filename(file.filename)
               file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/issue', filename))
               hash_set.append(sha256(UPLOAD_FOLDER+'/issue/'+filename))
      else : return "Submit more than 10 files."
      
      #print(hash_set)
      #issuer=current_identity
      hash_len=100
      tx_list=[]
      log=open("logs/log.txt","a")
      if len(hash_set)>hash_len:
         hash_list=[hash_set[i:i+hash_len] for i in range(0, len(hash_set), hash_len)]
         log.write(str(hash_list)+'\n')
         #print(hash_list)
         for i in hash_list:
            out=tx.tx_create(i)
            if out==False:
               return "Transaction failed."
            else: tx_list.append(out)
            print(out)
            sleep(1)
      else:
         #print(hash_set)
         log.write(str(hash_set)+'\n')
         out=tx.tx_create(hash_set)
         print(out)
         if out==False:
            return "Transaction Failed."
         else: tx_list.append(out)
         hash_set.clear()
      log.close()
      return {"Executed": tx_list}

api.add_resource(UserRegister, '/api/register')


if __name__ == '__main__':
   from db import db
   db.init_app(app)
   app.run(debug = True)
