from Modules.headerss import *
from Modules.log import *
from Modules.utils import *
from datetime import datetime, timedelta
import ctypes, sys, os, json
from concurrent.futures import ThreadPoolExecutor, as_completed

success = 0
failed = 0

db = 'Database/Members/Input'
os.makedirs(db, exist_ok=True)

def Title():
    global success, failed
    title = f'Asta Authorizer | Success: {success} | Failed: {failed}'
    if sys.platform == 'win32':
     ctypes.windll.kernel32.SetConsoleTitleW(title)

import re

def parse_token(fulltoken):
    try:
        if not fulltoken:
            return None

        # Split the full token by both ":" and "|" and clean the parts
        parts = re.split('[:|]', fulltoken)

        # Check every part's length to see if it's within the valid token length range
        for part in parts:
            part = part.strip()  # Clean up any spaces around the part
            if 50 < len(part) < 90:  # Valid token length check
                return part  # Return the valid token if it meets the length condition
        
        logger.info("No valid token found.")
        return None  # Return None if no valid token is found
    except Exception as e:
        logger.warning('Unable To Parse Token: %s', e)
        return None

class Authorizer():
    def __init__(self):
        self.config = load_config()

    def authorize(self, fulltoken, type):
        global success, failed


        if type == 'Offline':
            clientid = self.config['MemberBotSettings']['OfflineClientID']
            clientsecret = self.config['MemberBotSettings']['OfflineClientSecret']
            bott = self.config['MemberBotSettings']['OfflineToken']
        elif type == 'Online':
            clientid = self.config['MemberBotSettings']['OnlineClientID']
            clientsecret = self.config['MemberBotSettings']['OnlineClientSecret']
            bott = self.config['MemberBotSettings']['OnlineToken']
        else:
            logger.error('Invalid Type')
            return

        token = parse_token(fulltoken)
        if not token:
            logger.error('Token parsing failed.')
            return


        protocol = 'https://' if self.config['HostingSettings'].get('UseHTTPS') else 'http://'
        redirect = f"{protocol}{self.config['HostingSettings']['IPAddress']}:{self.config['HostingSettings']['BotPort']}"
        headers = get_auth_headers(client=clientid, redirect=redirect, token=token)

        json_data = {"authorize": "true"}
        url = f'https://discord.com/api/v9/oauth2/authorize?client_id={clientid}&response_type=code&redirect_uri={redirect}/callback&scope=identify%20guilds.join'

        session = make_session()
        code = None

        try:
            response = session.post(url=url, json=json_data, headers=headers)

            if response.status_code == 200:
                code = response.json()['location'].split('code=')[1]
            elif response.status_code == 401:
                failed += 1
                logger.error('Invalid Token', f'{token[:20]}**************')
                with open(f'{db}/{type}_invalid_token.txt', 'a') as f:
                    f.write(f'{fulltoken}\n')
            elif response.status_code == 429:
                failed += 1
                logger.error('Ratelimited Token', f'{token[:20]}**************')
                with open(f'{db}/{type}_ratelimited_token.txt', 'a') as f:
                    f.write(f'{fulltoken}\n')
            elif response.status_code == 403:
                failed += 1
                logger.error('Locked Token', f'{token[:20]}**************')
                with open(f'{db}/{type}_locked_token.txt', 'a') as f:
                    f.write(f'{fulltoken}\n')
            elif response.status_code > 499:
                failed += 1
                logger.error('Proxy Or Network Error', f'{token[:20]}**************')
                with open(f'{db}/{type}_proxy_error.txt', 'a') as f:
                    f.write(f'{fulltoken}\n')
        except Exception as e:
            failed += 1
            logger.error(f'Unknown Error: {str(e)}', f'{token[:20]}**************')
            with open(f'{db}/{type}_unknown_error.txt', 'a') as f:
                f.write(f'{fulltoken}\n')

        if not code:
            return

        # Prepare for token exchange
        headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        data = {
            'client_id': clientid,
            'client_secret': clientsecret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f'{redirect}/callback'
        }

        response = session.post(url='https://discord.com/api/v9/oauth2/token', data=data, headers=headers)

        if response.status_code == 200:
            access_token = response.json()['access_token']
            refresh_token = response.json()['refresh_token']
            expires_in = response.json().get('expires_in', 604800)
            expiry_time = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

            userid = get_user(access_token)
            logger.success('Successfully Authorized', f'{token[:20]}**************')

            json_path = f'{db}/{type}.json'

            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    try:
                        saved_data = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning(f'Corrupted JSON in {json_path}, initializing empty data.')
                        saved_data = {}
            else:
                saved_data = {}

            saved_data[userid] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiry": expiry_time
            }

            with open(json_path, 'w') as f:
                json.dump(saved_data, f, indent=4)

            with open(f'{db}/{type}_authed.txt', 'a') as f:
                f.write(f'{fulltoken}\n')

            success += 1
        else:
            failed += 1
            logger.error(f'Authorization Failed', f'{token[:20]}**************')
            with open(f'{db}/{type}_failed_auth.txt', 'a') as f:
                f.write(f'{fulltoken}\n')

        Title()

    def start(self, thread, type):
        with open(f'{db}/tokens.txt', 'r') as file:
            auths = [line.strip() for line in file if line.strip()]


        with ThreadPoolExecutor(max_workers=thread) as executor:
            futures = []

            for token in auths:
                if token:
                    futures.append(executor.submit(self.authorize, token, type))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error occurred in thread: {e}")

def auth_run():
    auth = Authorizer()
    threads = int(logger.input('Threads: '))
    type_input = logger.input('Type: ').lower()
    type = 'Offline' if 'of' in type_input else 'Online' if 'on' in type_input else None

    if not type:
        logger.warning('Invalid Type')
        return

    auth.start(threads, type=type)
    print(f'Asta Authorizer | Success: {success} | Failed: {failed}')
    input()
