from flask import Flask, render_template, request, redirect, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
from blockf import get_info
from time import sleep
import os
import hashlib
import tx_script as tx

def sha256(filename):
    BUF_SIZE = 65536  # read stuff in 64kb chunks!
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploader'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "fjsadf"

@app.route('/upload')
def index():
    return render_template('index.html')

@app.route('/verify')
def verify():
   return render_template('verifier.html')

@app.route('/invalid')
def inv():
   return 'Invalid input. Upload only .pdf certificates.'

@app.route('/exe')
def e():
   return 'Transaction executed.'

@app.route('/verifier', methods = ['POST'])
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

@app.route('/uploader', methods = ['POST'])
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
      hash_len=200
      tx_list=[]
      log=open("log.txt","a")
      if len(hash_set)>hash_len:
         hash_list=[hash_set[i:i+hash_len] for i in range(0, len(hash_set), hash_len)]
         log.write(str(hash_list)+'\n')
         #print(hash_list)
         for i in hash_list:
            out=tx.tx_create(i)
            if out==False:
               return redirect('/invalid')
            else: tx_list.append(out)
            print(out)
            sleep(1)
      else:
         #print(hash_set)
         log.write(str(hash_set)+'\n')
         out=tx.tx_create(hash_set)
         print(out)
         if out==False:
            return redirect('/invalid')
         else: tx_list.append(out)
         hash_set.clear()
      log.close()
      return {"Executed": tx_list}

if __name__ == '__main__':
   app.run(debug = True)
