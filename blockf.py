import requests
import json

def get_info(value):
    project_id="iJqHCFAtqLKBVreyBN42kUYmOqaNZd5G"

    param={'order':'desc','count':None}
    token={'project_id': project_id}

    r=requests.get("https://cardano-testnet.blockfrost.io/api/v0/metadata/txs/labels/20001", headers=token, params=param)

    j=json.loads(r.text)
    n=len(j)
    for i in range(n):
        if value in j[i]['json_metadata'].values():
            return {"True": j[i]['tx_hash']}
    return "False"
    
#print(get_info('01eb58709bc9bebf1b5f9ea347c599d52f84b407b3e4d1253a92ba49f84b40cb'))
