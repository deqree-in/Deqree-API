import json
import copy

root={
        "k": {"int": 0},
        "v": {"string":""}
      }

def convert(hash_set):
    with open('metadata.json') as f:
        metadata= json.load(f)
    c= open('uid_count.txt','r')
    uid=int(c.read())
    c.close()
    
    for hash in hash_set:
      uid+=1
      base=copy.deepcopy(root)
      base['k']["int"]=uid
      base['v']['string']=hash
      metadata['20001']['map'].append(base)

    c= open('uid_count.txt','w')
    c.write(str(uid))
    c.close()
    
    return metadata
