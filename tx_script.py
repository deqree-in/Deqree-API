#API Docs: https://input-output-hk.github.io/cardano-wallet/api
#Author: Advait Joglekar

import asyncio
import requests
import json
import jsonmeta as jm

with open('logs/payload.json') as f:
    payload= json.load(f)

wal_id='e7a99b9a9ad2743fa34074d1ef5a139776437a43'

async def tx_create(hash_set):
    pswd="bluecakeyummy"
    payload['passphrase']=str(pswd)
    payload['metadata']=jm.convert(hash_set)
    #print(payload['metadata'])
    
    try:
        r= requests.post(f"http://localhost:8090/v2/wallets/{wal_id}/transactions", json=payload)
    except: 
        return False
    
    j=json.loads(r.text)
    return j['id']
