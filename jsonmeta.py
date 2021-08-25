import json
import copy
from flask_jwt_extended import get_jwt_identity
from resources.user import UserModel

root={
        "k": {"int": 0},
        "v": {"string":""}
      }

def convert(hash_set):
    with open('logs/metadata.json') as f:
        metadata= json.load(f)
    c= open('logs/uid_count.txt','r')
    uid=int(c.read())
    c.close()
    
    user=UserModel.find_by_id(get_jwt_identity())
    issuer=user.username
    #print(issuer)
    
    issue={
        "k": {"string": "issuer"},
        "v": {"string": issuer}
      }
    
    metadata['40001']['map'].append(issue)

    for hash in hash_set:
      uid+=1
      base=copy.deepcopy(root)
      base['k']["int"]=uid
      base['v']['string']=hash
      metadata['40001']['map'].append(base)

    c= open('logs/uid_count.txt','w')
    c.write(str(uid))
    c.close()
    
    return metadata
