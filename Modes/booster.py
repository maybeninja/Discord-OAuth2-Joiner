from Modules.headerss import *
from Modules.log import *
from Modules.utils import *
from Modules.key import *
from flask import *
import time

class Booster():
    def __init__(self):
        self.config = load_config()
        self.redirect = f"{'https' if self.config['HostingSettings'].get('UseHTTPS') else 'http'}://{self.config['HostingSettings']['IPAddress']}:{self.config['HostingSettings']['BotPort']}"
        self.client_id = self.config['BoostingBotSettings']['BoostingBotClientID']
        self.client_secret = self.config['BoostingBotSettings']['BoostingBotClientSecret']
        self.bott = self.config['BoostingBotSettings']['BoostingBotToken']

    def authorise(self, fulltoken):
        token = parse_token(fulltoken)
        headers = get_auth_headers(token, self.client_id, self.redirect)
        json_data = {"authorize": "true"}
        url = f'https://discord.com/api/v9/oauth2/authorize?client_id={self.client_id}&response_type=code&redirect_uri={self.redirect}/callback&scope=identify%20guilds.join'

        session = make_session()
        code = None
        failed = 0

        try:
            response = session.post(url=url, json=json_data, headers=headers)
            if response.status_code == 200:
                code = response.json()['location'].split('code=')[1]
            elif response.status_code == 401:
                failed += 1
                logger.error('Invalid Token', f'{token[:20]}**************')
            elif response.status_code == 429:
                failed += 1
                logger.error('Ratelimited Token', f'{token[:20]}**************')
            elif response.status_code == 403:
                failed += 1
                logger.error('Locked Token', f'{token[:20]}**************')
            elif response.status_code > 499:
                failed += 1
                logger.error('Proxy Or Network Error', f'{token[:20]}**************')
        except Exception as e:
            failed += 1
            logger.error(f'Unknown Error: {str(e)}', f'{token[:20]}**************')

        if not code:
            return None

        headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f'{self.redirect}/callback'
        }

        response = session.post(url='https://discord.com/api/v9/oauth2/token', data=data, headers=headers)

        if response.status_code == 200:
            return response.json()['access_token']
        else:
            return None

    def add_user_boost(self, access_token, guild):
        session = make_session()
        json_data = {'access_token': access_token}
        userid = get_user(access_token)
        url = f"https://discord.com/api/v9/guilds/{guild}/members/{userid}"
        headers = {
            "Authorization": f"Bot {self.bott}",
            'Content-Type': 'application/json'
        }

        while True:
            response = session.put(url=url, headers=headers, json=json_data)
            if response.status_code in [204, 201]:
                logger.success(f'User {userid} Added', guild)
                return 'joined'
            elif response.status_code == 429:
                logger.warning(f'Rate limit hit for user {userid}, retrying...')
                time.sleep(1)
            else:
                logger.error(f"Failed to add user {userid}", str(response.content))
                return 'error'

    def boost(self, token, guild):
        session = make_session()
        headers = get_base_headers(token)
        r = session.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=headers)
        if r.status_code == 200:
            slots = r.json()
            if len(slots) != 0:
                used = 0
                for slot in slots:
                    if used >= 2:
                        break
                    slotid = slot['id']
                    payload = {"user_premium_guild_subscription_slot_ids": [slotid]}
                    r2 = session.put(f'https://discord.com/api/v9/guilds/{guild}/premium/subscriptions', headers=headers, json=payload)
                    if r2.status_code == 201:
                        used += 1
                        logger.success(f'Boosted {used} added to guild {guild}')
                    else:
                        logger.error('Boosting failed for one slot', str(r2.content))
                return 'success' if used > 0 else 'boost_failed'
            else:
                return 'no_slots'
        else:
            return 'slot_fetch_failed'

    def full_boost_process(self, fulltoken, guild_id):
        access_token = self.authorise(fulltoken)
        if not access_token:
            return 'auth_failed'

        # Step 2: Add user to guild (internally fetches user ID)
        result = self.add_user_boost(access_token, guild_id)
        if result != 'joined':
            logger.error("Failed to add user to guild.")
            return 'join_failed'

        boost_result = self.boost(fulltoken, guild_id)
        return boost_result
