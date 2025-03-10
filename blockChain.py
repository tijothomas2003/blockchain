from datetime import time
import hashlib
import json

class blockchain():
    def __init__(self,gen=False):
        if gen:
            self.blocks = []
        else:
            with open("blockChainDataBase.json",'r') as f:
                self.blocks = json.load(f)
        self.__secret = ''
        self.__difficulty = 4 
        i = 0
        while True:
            _hash = hashlib.sha256( str(i).encode('utf-8')).hexdigest()
            if(_hash[:self.__difficulty] == '0'*self.__difficulty):
                self.__secret = _hash
                break
            i+=1
    def create_block(self,sender_id="nil",user_name='nil',approver_id="nil",message="nil",role='nil',time="nil"):

        block = {
            'index': len(self.blocks),
            'user_name':user_name,
            'sender_id': sender_id,
            "approver_id":approver_id,
            "message":message,
            'role':role,
            "time":time,
            'timestamp': str(time)
        }
        if(block['index'] == 0):
            block['previous_hash'] = self.__secret # for genesis block
            #block['dis'] ="This is a genesis block"
        else:
            block['previous_hash'] = self.blocks[-1]['hash']
        i = 0
        while True:
            block['nonce'] = i
            _hash = hashlib.sha256(str(block).encode('utf-8')).hexdigest()
            if(_hash[:self.__difficulty] == '0'*self.__difficulty):
                block['hash'] = _hash
                break
            i+=1
        self.blocks.append(block)
        with open("blockChainDataBase.json",'w') as f:
            json.dump(self.blocks,f)
        return True
        
    def validate_blockchain(self):
        valid = True
        n = len(self.blocks)-1
        i = 0
        while(i<n):
            if(self.blocks[i]['hash'] != self.blocks[i+1]['previous_hash']):
                valid = False
                break
            i+=1
        if valid: return True
        else: return False

    def getAllMessage(self):
        
        with open("blockChainDataBase.json",'r') as f:
            self.blocks = json.load(f)
        check_block=[]
        for block in self.blocks:
           check_block.append(block)
        return check_block
    
    # def message_by_id(self,sender_id):
    #     check_block=[]
    #     for block in self.blocks:
    #         if block['sender_id']==sender_id:
    #             check_block.append(block)
    #     return check_block
