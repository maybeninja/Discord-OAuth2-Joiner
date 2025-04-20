import json
from Modules.headerss import *
from Modules.log import *
from Modules.utils import *
from typing_extensions import Literal
import time

db = 'Database/Members/Input/'


def remove_auth(userid: str, type: Literal['Offline', 'Online']):
    path = f"{db}{type}.json"
    
    if not os.path.exists(path):
        logger.warning(f"Auth file not found at {path}")
        return

    try:
        with open(path, 'r') as f:
            data = json.load(f)

        if userid in data:
            del data[userid]
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)

    except Exception as e:
        return

def add_user(userid, access_token, guild, type: Literal['Offline', 'Online']):
    try:
        session = make_session()
        config = load_config()
        bott = config['MemberBotSettings']['OfflineToken'] if type == 'Offline' else config['MemberBotSettings']['OnlineToken']
        json_data = {'access_token': access_token}
        url = f"https://discord.com/api/v9/guilds/{guild}/members/{userid}"
        headers = {
            "Authorization": f"Bot {bott}",
            'Content-Type': 'application/json'
        }

        while True:
            response = session.put(url=url, headers=headers, json=json_data)
            print(response.text, response.status_code)

            if response.status_code == 201:
                logger.success(f'User {userid} Added', guild)
                return 'joined'
            elif response.status_code == 204:
                logger.warning(f'User {userid} Already Added', guild)
                return 'already'
            elif 'banned' in response.text and 'user' in response.text:
                logger.warning(f'User {userid} Banned', guild)
                return 'banned'
            elif 'Unknown Guild' in response.text:
                logger.warning(f'Gateway Bot Not Added to Guild', guild)
                return 'gateway'
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 1)
                logger.warning(f'Rate Limit Exceeded, Retrying in {retry_after} seconds', guild)
                time.sleep(retry_after)
                continue
            elif response.status_code > 499:
                logger.warning(f'Network Error', 'Retrying')
                time.sleep(1)
                continue
            elif 'missing perm' in response.text:
                logger.error(f'Missing Permission', guild)
                return 'unauthorized'
            elif '100' in response.text:
                logger.error(userid, 'Max Guilds Reached')
                return 'maxguilds'
            elif 'unknown user' in response.text:
                logger.error(userid, 'Auth Expired')
                return 'expired'
            elif 'verified' in response.text:
                logger.error(userid, 'Auth Locked')
                return 'locked'
            else:
                logger.error(f"Failed with status: {response.status_code}", guild)
                return 'error'

    except Exception as e:
        print(f"Exception occurred: {e}")
        return 'error'


from datetime import datetime

# Track when the order starts
start_time = datetime.now()

from datetime import datetime

from datetime import datetime

def joiner(guildid, type: Literal['Offline', 'Online'], amount: int):
    path = f"{db}{type}.json"
    with open(path, 'r') as f:
        data = json.load(f)
    
    success = 0
    failed = 0
    already = 0
    order = get_order()
    
    # Track when the order starts
    start_time = datetime.now()

    # Prepare log file path for live progress
    live_order_file = f"Database/Members/Orders/{guildid}-{order}.txt"

    for userid, auth in data.items():
        access_token = auth.get("access_token")
        if not access_token:
            continue

        result = add_user(userid, access_token, guildid, type)

        if result == 'joined':
            success += 1
        elif result == 'already':
            already += 1
        elif result == 'unauthorized':
            break
        elif result == 'maxguilds':
            remove_auth(userid,type)
            failed += 1
        elif result == 'expired':
            remove_auth(userid,type)
            failed += 1
        elif result == 'locked':
            remove_auth(userid,type)
            failed += 1
        elif result == 'error':
            failed += 1
        elif result == 'gateway':
            break
        elif result == 'banned':
            break

        # Log running order progress to live.txt file
        elapsed_time = datetime.now() - start_time
        elapsed_seconds = int(elapsed_time.total_seconds())
        running_message = f"Order ID: {order} | Status: Running | Type: {type} | Started: {elapsed_seconds}s\n"
        with open(live_order_file, 'a') as file:
            file.write(running_message)

        if success == amount:
            break

    # After the order is complete, log the summary to the same file
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    elapsed_seconds = int(elapsed_time.total_seconds())
    
    completed_message = f"Order ID: {order} | Added: {success} | Already: {already} | Failed: {failed} | Total Time: {elapsed_seconds}s\n"
    with open(live_order_file, 'a') as file:
        file.write(completed_message)

    # Final logging for the complete order
    logger.info(f"Order ID: {order} | Success: {success} | Failed: {failed} | Already: {already} | Time: {elapsed_seconds}s")
