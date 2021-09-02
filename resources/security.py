from simple_file_checksum import get_checksum

def hash_gen(file_set:list, folder:str):
    hash_set=list()
    for filename in file_set:
            hash_set.append(get_checksum(folder+'/issue/'+filename,algorithm="SHA256"))
    return hash_set
