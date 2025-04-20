import tls_client , sys , os , random,base64 , json, re,time
from Modules.log import Logger
from Modules.utils import *
logger = Logger()
config = load_config()

proxymode = config.get('ProxyMode',False)


def load_proxies():
    try:
        with open("Input/proxies.txt", "r") as f:
            return [proxy.strip() for proxy in f.readlines() if proxy.strip()]
    except ValueError as v:
        logger.warning(f"PROXIES NOT FOUND",v)
        sys.exit(1)
        return []


def make_session():
     if proxymode:
          proxies = load_proxies()
          proxy = random.choice(proxies).strip()
          session = tls_client.Session(client_identifier='chrome_126',random_tls_extension_order=True,ja3_string=get_ja3())
          session.proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
          return session
     else:
          session = tls_client.Session(client_identifier='chrome_126',random_tls_extension_order=True,ja3_string=get_ja3())
          return session
     
     






class XSuper:
    def __init__(self) -> None:
        self.session = tls_client.Session(
            client_identifier="chrome_126", random_tls_extension_order=True
        )
        self.useragent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        )
        self.session.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://discord.com",
            "referer": "https://discord.com/login",
            "user-agent": self.useragent,
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "Asia/Calcutta",
        }

    def extract_asset_files(self):
        try:
            response = self.session.get("https://discord.com/login")
            pattern = r'<script\s+src="([^"]+\.js)"\s+defer>\s*</script>'
            matches = re.findall(pattern, response.text)
            if matches:
                return f"https://discord.com{matches[-1]}"
            return None
        except Exception as e:
            logger.warning(f"Unable to extract asset files: {e}")
            return None

    def get_build_number(self):
        try:
            asset_url = self.extract_asset_files()
            if not asset_url:
                return None

            response = self.session.get(asset_url)
            match = re.search(r'"buildNumber":(\d+)', response.text)
            if match:
                return match.group(1)
        except Exception as e:
            logger.warning(f"Unable to get build number: {e}")
        return None

    def build_super_properties(self):
        build_number = self.get_build_number() or "386432"  # Fallback if unavailable

        properties = {
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": self.useragent,
            "browser_version": "135.0.0.0",
            "os_version": "10",
            "referrer": "https://discord.com/channels/@me",
            "referring_domain": "discord.com",
            "release_channel": "stable",
            "client_build_number": int(build_number),
        }

        encoded = base64.b64encode(
            json.dumps(properties, separators=(",", ":")).encode()
        ).decode()

        return encoded


def get_ja3():
    plain_ja3 = '771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,13-27-65037-65281-45-43-35-16-10-18-11-51-23-0-5-17613,4588-29-23-24,0'
    try: 
         response = tls_client.Session(
                client_identifier="chrome_126", random_tls_extension_order=True
            ).get("https://tls.peet.ws/api/clean")
         if response.status_code == 200:
                ja3 = response.json().get("ja3", plain_ja3)
                return ja3
         else:
                return plain_ja3
    except Exception as e:
            return plain_ja3
    

def cookie():
        session = make_session()
    
        response = session.get("https://discord.com/api/v9/experiments")

        dcfduid = response.cookies.get("__dcfduid")
        sdcfduid = response.cookies.get("__sdcfduid")
        cfruid = response.cookies.get("__cfruid")
        return f"locale=en-US; __dcfduid={dcfduid}; __sdcfduid={sdcfduid}; __cfruid={cfruid}"



def get_auth_headers(token,client,redirect):
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
     
    headers = {
    "Accept": "*/*",
    "Accept-Encoding": "deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": token,
    "Content-Type": "application/json",
    "Cookie": cookie(),
    "Origin": "https://discord.com",
    "Priority": "u=1, i",
    "Referer": f"https://discord.com/oauth2/authorize?client_id={client}&redirect_uri={redirect}&response_type=code&scope=identify%20guilds.join",
    "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": useragent,
    "X-Debug-Options": "bugReporterEnabled",
    "X-Discord-Locale": "en-US",
    "X-Discord-Timezone": "America/Los_Angeles",
    "X-Super-Properties": XSuper().build_super_properties()

}

    return headers

def get_base_headers(token):
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
     
    headers = {
    "Accept": "*/*",
    "Accept-Encoding": "deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": token,
    "Content-Type": "application/json",
    "Cookie": cookie(),
    "Origin": "https://discord.com",
    "Priority": "u=1, i",
    "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": useragent,
    "X-Debug-Options": "bugReporterEnabled",
    "X-Discord-Locale": "en-US",
    "X-Discord-Timezone": "America/Los_Angeles",
    "X-Super-Properties": XSuper().build_super_properties()
    }
     
    return headers


def get_user(access_token, retries=3, delay=2):
    session = make_session()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    for attempt in range(retries):
        response = session.get("https://discord.com/api/v9/users/@me", headers=headers)

        if response.status_code == 200:
            return response.json().get("id")

        time.sleep(delay)  

    return None  
     
    
    

     