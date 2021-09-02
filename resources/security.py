from multiprocessing import Pool
from simple_file_checksum import get_checksum

def sha256(file:str):
        return get_checksum(file,algorithm="SHA256")

def hash_gen(file_set:list):
    hash_set=list()
    multi_process=Pool()
    hash_set=multi_process.map(sha256,file_set)
    '''for filename in file_set:
            hash_set.append(sha256(filename))'''
    return hash_set
