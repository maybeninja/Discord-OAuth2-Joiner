import yaml,sys,re
from Modules.log import Logger
import random , string,json
from typing_extensions import Literal
logger = Logger()









def parse_token(fulltoken):
    try:
        if not fulltoken:
            return None

        parts = re.split('[:|]', fulltoken)

        for part in parts:
            part = part.strip()  
            if 50 < len(part) < 90: 
                return part  
        
        logger.info("No valid token found.")
        return None 
    except Exception as e:
        logger.warning('Unable To Parse Token: %s', e)
        return None







def load_config():
    try:
        with open("config.yaml") as f:
            return yaml.safe_load(f)
        
    except Exception as e:
        logger.warning(f"UNABLE TO LOAD CONFIG FILE",e)
        sys.exit(1)
        return {}


def get_order(otype=None):
    if otype == None:
       order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
       return order_id
    else:
        pass



