import json , random , string , time , os 
from typing import List , Tuple , Dict , Any , Union , Optional , Sequence , Callable , TypeVar , Literal
from Modules.utils import *
db = 'Database/'
config = load_config()

mem = open(f"{db}Members/keys.json", 'a') 
boosts = open(f"{db}Boosts/keys.json", 'a')


def get_stock(type: Literal['Offline', 'Online', '1m', '3m'], service: Literal['members', 'boosts']):
    if service == 'boosts':
        path = f"{db}Boosts/Input/{type}_tokens.txt"
        if not os.path.exists(path):
            return 0
        try:
            with open(path, 'r') as f:
                tstock = len([line for line in f if line.strip()])
            return tstock
        except:
            return 0

    elif service == 'members':
        path = f"{db}Members/Input/{type}.json"
        if not os.path.exists(path):
            return 0

        try:
            with open(path, 'r') as f:
                data = json.load(f)
            stock = sum(1 for user in data.values() if user.get("access_token"))
            return stock
        except:
            return 0

   

def keygen(service: Literal['boosts', 'members'], type, amount):
    if service  == 'boosts':
        if amount % 2 != 0:
           return 'even amount only'

        stock = get_stock(type, service)
        bstock = stock/2
        if bstock < amount:
            return 'insufficia=ent'
        else:
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            path = f"{db}Boosts/keys.json"

            if not os.path.exists(path):
                mdb = {}
            else:
                with open(path, 'r') as bo:
                    try:
                        bdb = json.load(bo)
                    except json.JSONDecodeError:
                        bdb = {}

            bdb[key] = {
                'type': type,
                'amount': amount,
                'used': False,
            }

            with open(path, 'w') as bo:
                json.dump(bdb, bo, indent=4)

            return key
            


    if service == 'members':
        stock = get_stock(type, service)
        if stock < amount:
            return 'insufficient'
        else:
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            path = f"{db}Members/keys.json"

            if not os.path.exists(path):
                mdb = {}
            else:
                with open(path, 'r') as mem:
                    try:
                        mdb = json.load(mem)
                    except json.JSONDecodeError:
                        mdb = {}

            mdb[key] = {
                'type': type,
                'amount': amount,
                'used': False,
            }

            with open(path, 'w') as mem:
                json.dump(mdb, mem, indent=4)

            return key


def check_key(key):
    paths = [
        f"{db}Members/keys.json",
        f"{db}Boosts/keys.json"
    ]

    for path in paths:
        if not os.path.exists(path):
            continue

        try:
            with open(path, 'r') as f:
                data = json.load(f)
            if key in data and not data[key].get("used", True):
                return True
        except (json.JSONDecodeError, FileNotFoundError):
            continue

    return False




def gen_bulk(service: Literal['boosts', 'members'], type, amount, service_quantity):
    keys = []
    for _ in range(service_quantity):
        key = keygen(service, type, amount)

        # If keygen returns a non-16-character string, treat as error
        if not isinstance(key, str) or len(key) != 16:
            return key

        keys.append(key)

    return keys


def delete_key(key):
    paths = [
        f"{db}Members/keys.json",
        f"{db}Boosts/keys.json"
    ]

    for path in paths:
        if not os.path.exists(path):
            continue

        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            continue

        if key in data:
            del data[key]
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            return True  

    return False  





def get_auth_link(service,key,type=None):
    if service == 'members':
        if type == 'Offline':
            client_id = config['MemberBotSettings']['OfflineClientID']
        else:
            client_id = config['MemberBotSettings']['OnlineClientID']
    else:
        client_id = config['BoostingBotSettings']['BoostingBotClientID']
    
    protocol = 'https://' if config['HostingSettings'].get('UseHTTPS') else 'http://'
    redirect = f"{protocol}{config['HostingSettings']['IPAddress']}:{config['HostingSettings']['BotPort']}"
    auth_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=1&redirect_uri={redirect}/callback&response_type=code&scope=identify%20bot&state={key}"
    return auth_link


