def read_and_store():
    ids = []
    with open("users.txt",encoding="utf8") as file:
        ids = file.readlines()
    subs = 'ID'
    return [i for i in ids if subs in i]

def take_ids(res):
    res_2 = []
    for ele in res:
        ele_2 = ele.replace('ID', '').replace('-', '').replace('\n', '').strip()
        res_2.append(ele_2)
    return res_2

def get_users():
    return take_ids(read_and_store())