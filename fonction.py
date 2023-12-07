import json
import sqlite3
from time import sleep
from Trade import Trade

def open_json(path : str):
     with open(path, "r", encoding='utf-8') as read_file:
           dico = json.loads(read_file.read())
           return dico

def dump_json(path : str, dico):
    with open(path, "w") as write_file:
        json.dump(dico, write_file)
        
       
          
def create_db_tables(cur : sqlite3.Cursor , con : sqlite3.Connection):
    con.execute("PRAGMA foreign_keys = ON")
    cur.execute("CREATE TABLE IF NOT EXISTS users(uid INT PRIMARY KEY NOT NULL)")
    binder_request = "CREATE TABLE IF NOT EXISTS binder (card VARCHAR2 NOT NULL,nb_card INT NOT NULL,uid INT NOT NULL,searching BOOLEAN NOT NULL, FOREIGN KEY (uid)  REFERENCES users(uid) ON DELETE CASCADE)"
    cur.execute(binder_request)
    con.commit()

def connect_to_db(path_to_db : str):
    return sqlite3.connect(path_to_db)

def get_cursor(con : sqlite3.Connection):
    return con.cursor()

def request_to_list(request : str,request_param : tuple, cur : sqlite3.Cursor):
    list = []
    t = cur.execute(request,request_param)
    line = t.fetchone()
    while line:
        list.append(line[0])
        line = t.fetchone()
    return list
def request_to_list_of_tuple(request : str,request_param : tuple, cur : sqlite3.Cursor):
    list = []
    t = cur.execute(request,request_param)
    line = t.fetchone()
    while line:
        list.append(line)
        line = t.fetchone()
    return list

# def non_scalar_request(request : str, cur : sqlite3.Cursor, con : sqlite3.Connection):
#     cur.execute(request)
#     con.commit()


def user_exist(uid : str,cur : sqlite3.Cursor):
    # if(len(cur.execute("SELECT * FROM users WHERE uid = ?",(uid,)).fetchall()) <= 0):
    #     return False
    # else: 
    #     return True
    return not (len(cur.execute("SELECT * FROM users WHERE uid = ?",(uid,)).fetchall()) <= 0)
        
def add_card(card_name : str, nb : int, uid_str : str, searching: bool, con : sqlite3.Connection, cur : sqlite3.Cursor):
    return_code = 0 
    
    if (not user_exist(uid_str,cur)):
        x = add_user(uid_str,con,cur)
        if x == -1:
            return_code = -1
    try:
        request = cur.execute("SELECT nb_card FROM binder WHERE card = ? AND uid = ? AND searching = ? ",(card_name,uid_str,searching))
        request_result = request.fetchone()
        card_count : int
        if not request_result:
            card_count = 0 
        else:
            card_count = request_result[0]
            
        if card_count > 0:
            cur.execute("UPDATE binder SET nb_card = ? WHERE  card = ? AND uid = ? ", (card_count+nb,card_name,uid_str)) 
        else:
            cur.execute("INSERT INTO binder VALUES(lower(?),?,?,?)",(card_name,nb,uid_str,searching))
        con.commit()
    
    except Exception as e:
        print(f'error inserting card : {e}')
        con.rollback()
        return_code = -1 
        
    return return_code
  
def add_list(List : [str],uid : str,searching : int,con : sqlite3.Connection,cur : sqlite3.Cursor):
    if (not user_exist(uid,cur)):
        x = add_user(uid,con,cur)
        if x == -1:
            return -1
        
    cardName = open_json("cardName.json")["data"]
    unknown_cards = []
    didRegister = False
    for line in List:

        if line[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            nb_card = int(line.split(" ", 1)[0])

            card_name = line.split(" ", 1)[1]
            card_name = card_name[0:len(card_name)-1]

            if card_name.lower() in cardName:
                add_card(card_name,nb_card,uid,searching,con,cur)
                didRegister = True
            else:
                unknown_cards.append(card_name)

    if didRegister and len(unknown_cards) == 0:
        r = "all cards have been sucsesfully registered"
    elif didRegister:
        r = "cards have been sucsesfully registered but the following ones could not be found -> "
        r += ",".join(unknown_cards)
    else:
        r = "couldn't recognize any cards !"
    return r
     
def add_user(uid_str : str, con : sqlite3.Connection, cur : sqlite3.Cursor):
    try:
        cur.execute("INSERT INTO users VALUES(?)",(uid_str,))
        con.commit()
    except:
        print("error inserting user")
        return -1
    
def remove_card(uid_str : str, card_name : str ,nb : int, con : sqlite3.Connection, cur : sqlite3.Cursor ):
    return_code : int 
    try:
        request = cur.execute("SELECT nb_card FROM binder WHERE card = ? AND uid = ? ",(card_name,uid_str))
        card_count = request.fetchone()[0]
        if card_count > nb:
            cur.execute("UPDATE binder SET nb_card = ? WHERE  card = ? AND uid = ? ", (card_count-nb,card_name,uid_str)) 
            return_code = 0
        else:  
            cur.execute("DELETE FROM binder WHERE card = ? AND uid = ? ",(card_name,uid_str))
            return_code = 1
            
        con.commit()
        return return_code
    
    except Exception as e : 
        print(f'error deleting card : {e}')
        con.rollback()
        return -1
   
def clear_binder_by_category(uid : str,searching : int,con : sqlite3.Connection, cur : sqlite3.Cursor ):
    try:
        cur.execute("DELETE FROM binder WHERE uid = ? AND searching = ?",(uid,searching))
        con.commit()
        return 0 
    except Exception as e:
        print(f'errror clearing binder : {e}')
        con.rollback()
        return -1 
    

    
def get_binder(uid : str,cur : sqlite3.Cursor):
    r = {"searching" : [], "owned" : []}
    request_searching = "SELECT card, nb_card FROM binder WHERE uid = ? AND searching = ?"
    request_owned = "SELECT card, nb_card FROM binder WHERE uid = ? AND searching = ?"

    r["searching"] = request_to_list_of_tuple(request_searching, (uid,1),cur)
    r["owned"] = request_to_list_of_tuple(request_owned,(uid,0),cur)
    return r


   
def look_for_trades(uid : str , cur : sqlite3.Cursor):
    binder = get_binder(uid,cur)
    trades : [Trade] = []
    query = """
        SELECT uid
        FROM binder
        WHERE uid != ? AND searching = 0 AND card IN (
            SELECT card
            FROM binder
            WHERE uid = ? AND searching = 1
        )
        AND uid IN (
            SELECT uid
            FROM binder
            WHERE searching = 1 AND card IN (
                SELECT card
                FROM binder
                WHERE uid = ? AND searching = 0
            )
        )
        """
    uid_users_can_trade_with = request_to_list(query,(uid,uid,uid),cur) 
     
    for trader_id in uid_users_can_trade_with:
        query = """
            SELECT card FROM binder WHERE uid = ?
            AND searching = 1 
            AND card IN(SELECT card FROM binder WHERE uid = ? AND searching = 0
            )
        """
        my_cards : [] = request_to_list(query,(trader_id,uid),cur)
        trader_cards : [] = request_to_list(query,(uid,trader_id),cur)
        trades.append(Trade(int(uid), int(trader_id), my_cards,trader_cards))
    return trades

def lower_binder(uid : str, con : sqlite3.Connection, cur : sqlite3.Cursor):
    try:
        cur.execute("UPDATE binder SET card = lower(card) WHERE uid = ?",(uid,))
        con.commit()
    except Exception as e:
        con.rollback()
        print("error lowering binder : " + e)
        return -1
    return 0