import json
def open_json(path : str):
     with open(path, "r", encoding='utf-8') as read_file:
           dico = json.loads(read_file.read())
           return dico

def dump_json(path : str, dico):
    with open(path, "w") as write_file:
        json.dump(dico, write_file)

def insert_data(nom_carte : str, nbr_carte : int, string_user_id : str, WhishOrHave : str):
    dico = open_json("data.json")

    if string_user_id not in dico:
       create_user_collection(string_user_id)
       dico = open_json("data.json")

    if nom_carte not in dico[string_user_id][WhishOrHave]:
        dico[string_user_id][WhishOrHave].update( { nom_carte : {"nbr" : 0 }  } )
        dico[string_user_id][WhishOrHave][nom_carte]["nbr"] = nbr_carte
    else:
        dico[string_user_id][WhishOrHave][nom_carte]["nbr"] += nbr_carte
        
  
    dump_json("data.json",dico)
   
def overwrite_data(nom_carte : str, nbr_carte : int, string_user_id : str, WhishOrHave : str):
    dico = open_json("data.json")
    dico[string_user_id][WhishOrHave].clear()
    if string_user_id not in dico:
       create_user_collection(string_user_id)
       dico = open_json("data.json")

    if nom_carte not in dico[string_user_id][WhishOrHave]:
        dico[string_user_id][WhishOrHave].update( { nom_carte : {"nbr" : 0 }  } )
        dico[string_user_id][WhishOrHave][nom_carte]["nbr"] = nbr_carte
    else:
        dico[string_user_id][WhishOrHave][nom_carte]["nbr"] += nbr_carte
        
  
    dump_json("data.json",dico)
   

def create_user_collection(user_id : str):
    dico = open_json("data.json")
    dico.update( { user_id : {"wish" : {}, "have" : {}}} )
    dump_json("data.json",dico)