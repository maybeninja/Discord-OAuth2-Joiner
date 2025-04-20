from Modules.headerss import *
from Modules.log import *
from Modules.utils import *
from Modules.key import *
from Modes.adder import *
from flask import *
import threading

import re


auto = Flask(__name__)
config = load_config()

site = config['AutobuySupport']['Site']
if site.lower() != 'sellauth':
    logger.warning('Incorrect Autobuy Site')
    sys.exit(1)




@auto.route('/sellauth', methods=['POST'])
def sellauth():
    data = request.json
    invoice_id = data.get("invoice_id")
    email = data.get("email")
    quantity = data.get("item", {}).get("quantity")
    product_name = data.get("item", {}).get("product", {}).get("name")
    variant_name = data.get("item", {}).get("variant", {}).get("name")

    final_product_name = variant_name if variant_name and variant_name.lower() != "default" else product_name

    if 'offline' in final_product_name.lower():
        type = 'Offline' 
        service = 'members'
        amount = quantity
        stock = get_stock(type, service)
        if stock < amount:
            return 'Insufficient Stock'
        key = keygen(service, type, amount)
        link = get_auth_link(service,key,type)
        delivery = f"Service: Offline Members\nQuantity: {amount}\n Key: {key}\nBot Link: {link}"
        return delivery

    elif 'online' in final_product_name.lower():
        type = 'Online'
        service = 'members'
        amount = quantity
        stock = get_stock(type, service)
        if stock < amount:
            return 'Insufficient Stock'
        key = keygen(service, type, amount)
        link = get_auth_link(service,key,type)
        delivery = f"Service: Offline Members\nQuantity: {amount}\n Key: {key}\nBot Link: {link}"
        return delivery

    elif 'boost' in final_product_name.lower():
        service = 'boosts'

        if '3' in final_product_name:
            type = '3m'
        else:
            type = '1m'

        numbers = re.findall(r'\d+', final_product_name)
        amount = next((int(n) for n in numbers if int(n) % 2 == 0 and int(n) > 0), None)

        if not amount:
            return 'Invalid boost quantity'

        stock = get_stock(type, service)
        bstock = stock / 2

        if bstock < amount:
            return 'Insufficient Stock'

        key = keygen(service, type, amount)
        link = get_auth_link(service,key)
        delivery = f"Service: Offline Members\nQuantity: {amount}\n Key: {key}\nBot Link: {link}"
        return delivery

    return {'error': 'Invalid product name or configuration'}




import json
import os
bdb = 'Database/Boosts/keys.json'
mbd = 'Database/Members/keys.json'

# Lock for thread-safe JSON file operations
lock = threading.Lock()

# Function to load JSON data safely
def load_json_safe(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return {}
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# Function to save data to JSON file
def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)



# Callback route
@auto.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    key = request.args.get('state')
    guild_id = request.args.get('guild_id')

    # Lock the critical section for reading and writing JSON files
    with lock:
        # Load JSON files safely
        boost_keys = load_json_safe(bdb)
        member_keys = load_json_safe(mbd)

        # Check if the key exists in either boost_keys or member_keys
        if key in boost_keys:
            key_data = boost_keys[key]
            service = 'boosts'
        elif key in member_keys:
            key_data = member_keys[key]
            service = 'members'
        else:
            return jsonify({"status": "incorrect"}), 400

        # If the key has already been used, return error
        if key_data.get('used'):
            return jsonify({"status": "used"}), 403

        # Call joiner if service is 'members'
        if service == 'members':
            joiner(
                guildid=guild_id,
                type=key_data.get('type', 'Offline'),
                amount=key_data.get('amount', 1)
            )

        # Mark the key as used
        key_data['used'] = True
        
        # Save the updated JSON data with the key marked as used
        if service == 'boosts':
            boost_keys[key] = key_data
            save_json(bdb, boost_keys)
        else:
            member_keys[key] = key_data
            save_json(mbd, member_keys)

    # Return the success response
    return jsonify({
        "status": "success",
        "service": service,
        "type": key_data.get("type"),
        "amount": key_data.get("amount"),
        "used": True
    }), 200
   
def start():
 if config['AutobuySupport']['Enable']:
    auto.run(threaded=True,host=config['HostingSettings']['Host'], port=config['HostingSettings']['AutobuyPort'])
